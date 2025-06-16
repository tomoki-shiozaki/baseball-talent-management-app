def calc_avg(data_dict):
    """
    月ごとの値のリストを受け取り、平均を計算して返す。
    例: {month1: [6.2, 6.3], month2: [6.1]} → {month1: 6.25, month2: 6.1}
    """
    return {
        month: round(sum(vals) / len(vals), 2)
        for month, vals in data_dict.items()
        if vals
    }
