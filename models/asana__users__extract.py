import alto.engine
import duckdb
import pyarrow as pa


def model(dbt, session: duckdb.DuckDBPyConnection):
    engine = alto.engine.get_engine(dbt.config.get("target_name"))
    # Setup pipeline
    (tap,) = alto.engine.make_plugins(
        "tap-asana",  # 👈 could be 1 of 100s of taps
        filesystem=engine.filesystem,
        configuration=engine.configuration,
    )
    # Extract 1 specific stream based on the schema.yml 👀
    tap.select = [dbt.config.get("source_stream")]
    # Run pipeline
    py_buf, batch_size = [], 50_000
    table = None
    with alto.engine.tap_runner(
        tap,
        engine.filesystem,
        engine.alto,
        state_key=dbt.this.identifier,
    ) as output_stream:
        for record in output_stream:
            if record["type"] != "RECORD":
                continue
            py_buf.append(record["record"])
            if len(py_buf) == batch_size:
                if table is None:
                    table = session.from_arrow(pa.Table.from_pylist(py_buf))
                else:
                    table = table.union(
                        session.from_arrow(pa.Table.from_pylist(py_buf))
                    )
                py_buf.clear()
    if py_buf:  # Flush remaining records
        if table is None:
            table = session.from_arrow(pa.Table.from_pylist(py_buf))
        else:
            table = table.union(session.from_arrow(pa.Table.from_pylist(py_buf)))
    # Return data
    return table
