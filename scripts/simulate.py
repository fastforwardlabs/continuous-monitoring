'''
1. Score Train Data - this provides evaluation data in Evidently.ai
2. Run simulation - for every N=2 months that pass (starting with data split date):
    - Query prod_df for new listings (date_listed) and score it using deployed model
    - Query prod_df for newly sold properties (date_sold) and use cdsw.track_metric() to assign ground truth to stored prediction
    - Query CML Metric Store for those newly sold properties, generate dataframe, and then a new evidently report
    - Deploy updated Evidently dashboards (data drift & regression metrics) for newly sold properties
    - Wait a bit, maybe...

'''




