from pathlib import Path
import tempfile
from datavolley import read_dv


def save_uploaded_file_temporarily(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name


def parse_dvw_file(temp_path: str):
    dv = read_dv.DataVolley(temp_path)
    plays = dv.get_plays()
    return plays