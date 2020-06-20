class Adjacency:

  def __init__(self, mat):
    self.mat = mat

  def compress_row_col(self, mat, bids, label, ROW_COL='both'):
    # Compresses rows, columns, or both, by summing all elements specified in bids
    # The typical use case is to combine pre or post synapses of a given type.
    # E.g., compress_row_col(orn_bids, 'ORNs') yields a matrix where all ORNs 
    # have been summed into a single row/column.
    ROW = (ROW_COL == 'row')
    COL = (ROW_COL == 'col')
    if ROW_COL == 'both':
      ROW = True
      COL = True
    
    if ROW:
      pre_sum = pd.DataFrame(mat.loc[bids,:].sum(axis=0), columns = [label]).transpose()
      mat = pd.concat([mat, pre_sum], axis=0)
      mat = mat.drop(bids, axis=0)
    if COL:
      post_sum = pd.DataFrame(mat.loc[:,bids].sum(axis=1), columns = [label])
      mat = pd.concat([mat, post_sum], axis=1)
      mat = mat.drop(bids, axis=1)
    return mat
  
  def compress_matrix(self, mat, type_bids, ROW_COL ='both', MERGE_REST = True):
    # Uses 'compress_row_col' to completely compress the matrix.
    # type_bids is a dict of bids

    named_bids = list()
    for key in type_bids.keys():
      mat = self.compress_row_col(mat, type_bids[key], key, ROW_COL)
      named_bids += list(type_bids[key])

    if MERGE_REST:
      rest_bids = list(set(self.mat.index) - set(named_bids))
      mat = self.compress_row_col(mat, rest_bids, 'rest', ROW_COL)
    return mat

  # TODO: tidy up plotting fns, return fig objects.
  def heatmap(self, mat, LOG_SCALING = True):
    # Simple heatmap function with option for log scaling, default is True.
    # mat is an input, so compression happens outside this fn.

    if LOG_SCALING:
      mat = np.log(mat)

    plt.imshow(mat)
    # plt.colorbar()
    plt.title('Log connection strength', fontsize=20)
    plt.xticks(np.arange(mat.shape[1]), mat.columns, fontsize=11, rotation=45)
    plt.yticks(np.arange(mat.shape[0]), mat.index, fontsize=14)
    return plt.gcf()

  def piechart(self, bids, type_bids, PRE_POST ='both', MERGE_REST = True, fig = None, axs = None):
    # Plots pie chart of connectivity for 'bids'. Charts will be sums over bids 
    # more than one body ID is given.
    #
    # bids          - int, or list/array/series of ints. Body ID(s) for neurons 
    #                 of interest. 
    # type_bids     - dict of partner type body IDs. All partner body IDs must  
    #                 be present in self.mat.
    # PRE_POST      - 'pre', 'post', 'both' (default). Specifies whether to  
    #                 create plots for upstream partners, downstream partners,
    #                 or both (default). 
    # MERGE_REST    - logical. True (default), if set to false partners not 
    #                 present in type_bids will not be included on the plot.
    # fig, axs      - Optional figure / axes objects. Useful for constructing 
    #                 larger subplot arrays. 

    PRE = (PRE_POST == 'pre')
    POST = (PRE_POST == 'post')
    if PRE_POST == 'both':
      PRE = True
      POST = True
      if fig is None:
        fig, axs = plt.subplots(1, 2)
    else:
      if fig is None:
        fig, axs = plt.subplots(1, 1)
        axs = [axs]
    
    if PRE:
      cmat = self.compress_matrix(self.mat, type_bids, ROW_COL='row', MERGE_REST = MERGE_REST)
      pre_vals = np.array(cmat.loc[:,bids])
      if pre_vals.ndim == 2:
        pre_vals = pre_vals.sum(axis=1)
      axs[0].pie(pre_vals, labels = cmat.index)
      axs[0].set_title('Pre \n(upstream)')

    if POST:
      cmat = self.compress_matrix(self.mat, type_bids, ROW_COL='col', MERGE_REST = MERGE_REST)
      post_vals = np.array(cmat.loc[bids,:])
      if post_vals.ndim == 2:
        post_vals = post_vals.sum(axis=0)
      axs[-1].pie(post_vals, labels = cmat.columns)
      axs[-1].set_title('Post \n(downstream)')
    axs[-1].legend(loc="center left", bbox_to_anchor=(1.1, 0, 0.4, 1.1))
    
    plt.rc('figure', figsize = (8,8))
    plt.rc('font', size = 14)
    plt.rc('axes', titlesize = 18)
    plt.rc('figure', titlesize = 28)
    fig.subplots_adjust(top=1.25)
    
    return fig, axs
  def stacked(self, bids, type_bids, PRE_POST ='both', MERGE_REST = True, SUM_BIDS = False, fig = None, axs = None):
    # Plots stacked barplots for connectivity for 'bids'. 
    #
    # bids          - int, or list/array/series of ints. Body ID(s) for neurons 
    #                 of interest. 
    # type_bids     - dict of partner type body IDs. All partner body IDs must  
    #                 be present in self.mat.
    # PRE_POST      - 'pre', 'post', 'both' (default). Specifies whether to  
    #                 create plots for upstream partners, downstream partners,
    #                 or both (default). 
    # MERGE_REST    - logical. True (default), if set to false partners not 
    #                 present in type_bids will not be included on the plot.
    # SUM_BIDS      - logical. False (default), if true a single bar plot will 
    #                 be returned that is a sum over bids.
    # fig, axs      - Optional figure / axes objects. Useful for constructing 
    #                 larger subplot arrays. 

    PRE = (PRE_POST == 'pre')
    POST = (PRE_POST == 'post')
    if PRE_POST == 'both':
      PRE = True
      POST = True
      if fig is None:
        fig, axs = plt.subplots(2, 1)
    else:
      if fig is None:
        fig, axs = plt.subplots(1, 1)
        axs = [axs]
    
    if PRE:
      cmat = self.compress_matrix(self.mat, type_bids, ROW_COL='row', MERGE_REST = MERGE_REST)
      cmat.loc[:,bids].transpose().plot.bar(stacked=True, width=0.9, ax = axs[0])
      axs[0].set_title('Pre (Upstream)')
      if POST:
        axs[0].set_xticks([])

    if POST:
      cmat = self.compress_matrix(self.mat, type_bids, ROW_COL='col', MERGE_REST = MERGE_REST)
      cmat.loc[bids,:].plot.bar(stacked=True, width=0.9, ax = axs[-1])
      axs[-1].set_title('Post (Downstream)')
      axs[-1].legend([])
      if PRE == False:
        axs[0].set_xticks([])
        axs[0].legend(loc="center left", bbox_to_anchor=(1, 0, 0.4, 1.1))

    axs[0].legend(loc="center left", bbox_to_anchor=(1, 0, 0.4, 1.1))
    plt.rc('figure', figsize = (8,8))
    plt.rc('font', size = 14)
    plt.rc('axes', titlesize = 18)
    plt.rc('figure', titlesize = 28)
    fig.subplots_adjust(top=1.25)
    
    return fig, axs