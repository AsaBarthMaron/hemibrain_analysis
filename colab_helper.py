import pandas as pd

def worksheet_to_df(worksheet, data_inds):
  df = worksheet.get_all_values()
  df = pd.DataFrame(df)
  df.columns = df.iloc[0] # Assumes column names are in first row of worksheet.
  df = df.iloc[data_inds] # Keep only the data
  return df

def square_matrix(partner_bids, partner_cons = None):
  
  # Pull data if necessary
  if partner_cons is None:
    partner_cons = neuprint.fetch_adjacencies(sources=partner_bids, \
                                            targets=partner_bids, \
                                            min_total_weight=1, \
                                            rois='AL(R)')[1]
  mat = neuprint.utils.connection_table_to_matrix(partner_cons)

  # Convert to a square matrix, because I'm not insane.
  # Add back missing rows
  missing_bids = list(set(partner_bids) - set(mat.index)) 
  missing_cons = np.zeros((len(missing_bids), mat.columns.shape[0]))
  missing_cons = pd.DataFrame(missing_cons, columns=mat.columns, index=missing_bids)
  mat = pd.concat([mat, missing_cons], axis=0)
  # Add back missing columns
  missing_bids = list(set(partner_bids) - set(mat.columns)) 
  missing_cons = np.zeros((mat.index.shape[0], len(missing_bids)))
  missing_cons = pd.DataFrame(missing_cons, columns=missing_bids, index=mat.index)
  mat = pd.concat([mat, missing_cons], axis=1)
  # Resort to order in partner_bids.
  mat = mat.loc[partner_bids, partner_bids]
  return mat
