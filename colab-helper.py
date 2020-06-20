def worksheet_to_df(worksheet, data_inds):
  df = worksheet.get_all_values()
  df = pd.DataFrame(df)
  df.columns = df.iloc[0] # Assumes column names are in first row of worksheet.
  df = df.iloc[data_inds] # Keep only the data
  return df