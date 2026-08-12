from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = (BASE_DIR / "data_set")

AED_DIR = (DATA_DIR / "01_AED")

BOUNDARY_DIR = (DATA_DIR / "02_집계구경계")

CENSUS_POP_DIR = (DATA_DIR / "03_집계구인구")

GRID_POP_DIR = (DATA_DIR / "04_100M격자인구")

GRID_BORDER_DIR = (DATA_DIR / "05_100M격자경계")

CARDIAC_DIR = (DATA_DIR / "06_심정지통계")

RESULT_DIR = (DATA_DIR / "07_분석결과")


RESULT_DIR.mkdir(parents=True, exist_ok=True,)

AED_FILE = (AED_DIR / "aed_raw.csv")

CENSUS_FILE = (BOUNDARY_DIR / "bnd_oa_00_2025_2Q.shp")

DONG_FILE = (BOUNDARY_DIR / "bnd_dong_00_2025_2Q.shp")

SIGUNGU_FILE = (BOUNDARY_DIR / "bnd_sigungu_00_2025_2Q.shp")

SIDO_FILE = (BOUNDARY_DIR / "bnd_sido_00_2025_2Q.shp")

TARGET_CRS = "EPSG:5179"


ACCESS_DISTANCES = [100, 200, 300,]

SEOUL_CODE = "11"

MIN_POPULATION = 100

TOTAL_POP_CODE = "to_in_001"

AGE_65_CODES = [
    "in_age_014",  # 65~69
    "in_age_015",  # 70~74
    "in_age_016",  # 75~79
    "in_age_017",  # 80~84
    "in_age_018",  # 85~89
    "in_age_019",  # 90~94
    "in_age_020",  # 95~99
    "in_age_021",  # 100세 이상
]