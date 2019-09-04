results = results.sample(frac=1).reset_index(drop=True)
train = results[::2]
test = results[1::2]

clfs = {}
for name, group in train.groupby("y"):
    clfs[name] = XGBRegressor(n_estimators=1000).fit(group[X_cols], group["size"])

tot_real = 0
tot_best = 0
singles = defaultdict(list)
singles_totals = defaultdict(int)
preds = []
preds_total = 0
preds2 = 0
for name, group in test.groupby("fname"):
    X = group[X_cols].iloc[0, :]
    real = None
    best_score = 1000000000000000
    best = group.iloc[0]["bestvalue"]
    other_pred = clf.predict(group[X_cols])[0]
    for compr in group["y"]:
        if compr == other_pred:
            preds.append(group[group["y"] == compr].iloc[0]["size"])
            preds_total += best
        size = clfs[compr].predict(pd.DataFrame([X]))
        score = size[0]
        if score < best_score:
            best_score = score
            real = (compr, group[group["y"] == compr].iloc[0]["size"])
        singles[compr].append(group[group["y"] == compr].iloc[0]["size"])
        singles_totals[compr] += best
        # print(compr, size)
    if real is None:
        continue
    print("real", *real, "best", group.iloc[0]["bestclass"], best)
    preds2 += group.iloc[np.argmin(clf2.predict(group[list(X_cols) + ["y_num"]]))]["size"]
    tot_real += real[1]
    tot_best += best

print("real best", tot_real / tot_best)
print("pred", sum(preds) / preds_total)
print("pred2", preds2 / tot_best)

for x in singles:
    print("single", x, len(singles[x]), np.sum(singles[x]) / singles_totals[x])

# real best 1.245773020013956
# pred 1.0395065733041673
# pred2 1.1996759134383648
# single pyarrow brotli 869 1.8381558884612954
# single csv zip 847 1.728631784369642
# single csv None 893 6.298328760353326
# single pyarrow snappy 867 2.4194515020899625
# single csv xz 901 1.0967102041370123
# single csv bz2 853 1.168023920566413
# single pyarrow None 841 4.385563484712902
# single csv gz 849 1.4153226917538795
# single fastparquet GZIP 878 1.7205823976917411
# single fastparquet UNCOMPRESSED 896 8.05438194800453
# single pyarrow gzip 859 1.6972725798618562
# CPU times: user 27.6 ms, sys: 6 µs, total: 27.6 ms
# Wall time: 42.6 ms
