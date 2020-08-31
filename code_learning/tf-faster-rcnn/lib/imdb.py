class imdb(object):
  """Image database."""
  def __init__(self, name, classes=None):
    self._name = name
    self._num_classes = 0  # len(_classes)
    if not classes:   # classes只读属性
      self._classes = []
    else:
      self._classes = classes  # 类别名列表
    self._image_index = []
    self._obj_proposer = 'gt'
    self._roidb = None
    self._roidb_handler = self.default_roidb  # 可指定
    # Use this dict for storing dataset specific config options
    self.config = {}


  @property
  def name(self):
    return self._name

  @property
  def num_classes(self):
    return len(self._classes)

  @property
  def classes(self):
    return self._classes

  @property
  def image_index(self):
    return self._image_index

  @property
  def roidb_handler(self):
    return self._roidb_handler

  @roidb_handler.setter
  def roidb_handler(self, val):
    self._roidb_handler = val
  
  @property
  def roidb(self):
    # A roidb is a list of dictionaries, each with the following keys:
    #   boxes
    #   gt_overlaps
    #   gt_classes
    #   flipped
    if self._roidb is not None:
      return self._roidb
    self._roidb = self.roidb_handler()
    return self._roidb

  @property
  def cache_path(self):
    cache_path = osp.abspath(osp.join(cfg.DATA_DIR, 'cache'))
    if not os.path.exists(cache_path):
      os.makedirs(cache_path)
    return cache_path

  @property
  def num_images(self):
    return len(self.image_index)

  def image_path_at(self, i):
    raise NotImplementedError

  def default_roidb(self):
    raise NotImplementedError






























  
