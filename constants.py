COLUMN_IDENTIFIER = {
    "Annual": {
        "pattern": r"\d{4}",
        "separator": " "
    },
    "Quarterly": {
        "pattern": r"\d{4}Q\d{1}",
        "separator": "Q",
        "frequency": 4
    },
    "Monthly": {
        "pattern": r"\d{4}-\d{2}",
        "separator": "-",
        "frequency": 12
    }
}
