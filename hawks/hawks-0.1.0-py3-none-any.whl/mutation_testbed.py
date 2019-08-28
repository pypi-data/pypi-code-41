import pandas as pd
import hawks

obj = hawks.create_generator()

indiv_df = pd.DataFrame()
ari_df = pd.DataFrame()

for i in range(num_runs):
    init_sw = indiv.evaluate()
    indiv = hawks.create_individual()

    for j in range(num_muts):

        indiv.mutate()

        sw = indiv.evaluate()
        constraints = indiv.calc_constraints()
        df.append(
            {
            "run": i,
            "step": j,
            "sw" : sw
            },
            ignore_index=True
        )
        # Add constraint values too
        if j % clust_step == 0:
            # Run clustering algs

            # Append to ari_df
        