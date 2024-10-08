import numpy as np
import pandas as pd

import JK13.LoadMatlabFuncs as LoadMatlabFuncs
import Modules.Funcs as Funcs
#import LoadMatlabFuncs

np.set_printoptions(precision = 2)
#pd.set_option('display.precision', 2)


def scalefeatures(vals):
  return vals * 2.0 - 0.05

class JK13(object):
  """
  General informational class, with a few
  useful methods.
  """
  possible_hues = np.arange(0, 0.9, 0.15)
  conditions = ['Positive','Negative','Neutral']
  features = ['Hue','Length','Saturation']

  @classmethod
  def getfeatures(cls, df):
    return df[cls.features].values



class JK13Participant(JK13):

  def __init__(self, filepath):
    self.filepath = filepath

    matlab_data = LoadMatlabFuncs.loadmat(filepath)
    self.userps = matlab_data['userps']
    self.guips = matlab_data['guips']

    self._extract_generation()
    self._extract_training()
    self._pandify()


  def _extract_generation(self):
    """
    Extract generated categories from the matlab data...
    """

    # newcrystaldata is a list with two sublists.
    # each sublist has three, 8x3 arrays, like so:
    #
    # 	[ [[8x3],[8x3],[8x3]], [[8x3],[8x3],[8x3]] ]
    newcrystaldata = self.userps['newcrystaldata']

    # sometimes the second list of arrays is not there.
    # Alan Jern only ever uses the first one anyway, so
    # I'll remove it..
    if len(newcrystaldata) == 2:
      newcrystaldata = newcrystaldata[0]

    # I do not know what all of the rows are for. In Alan
    # Jern's code, the generated category statistics are
    # computed using rows 3-8. Those must be the 6 items
    # generated by participants...
    newcrystaldata = [i[2:,:] for i in newcrystaldata]

    # concatenate the subarrays to make a 6x3x3 array
    # 	[item, feature, condition]
    newcrystaldata = [np.expand_dims(i, 2) for i in newcrystaldata]
    newcrystaldata = np.concatenate(newcrystaldata, axis = 2)

    self.generation = newcrystaldata


  def _extract_training(self):
    """
    Extract the experimenter-defined categories
    from the matlab data.

    Each of 3 conditions has different categories of 4 exemplars
    There were two categories per condition.

    the feature values are all stored in different spots...
    """


    # len is a list of three lists, one for each condition
    # ech condition has two arrays with four elements,
    # corresponding to the category exemplar lengths
    #
    # lengths is item, category, condition
    lengths = np.empty((4, 2, 3))
    for condition, categories in enumerate(self.guips['crystal']['len']):
      lengths[:,:,condition] = (
        np.concatenate([np.expand_dims(i, 1) for i in categories], axis=1)
        )

    # saturation is the same story as length, but each array is a
    # has HSV values for each exemplar, with the hue set to 0.
    saturations = np.empty((4, 2, 3))
    for condition, categories in enumerate(self.guips['crystal']['color']):
      for category, exemplars in enumerate(categories):
        saturations[:,category,condition] = (
          # np.concatenate([np.expand_dims(i[1], 1) for i in exemplars])
          # kesong: fix dimension error, assuming dim 0 instead of 1
          np.concatenate([np.expand_dims(i[1], 0) for i in exemplars])
        )

    # the hue values are shuffled per participant, with the possible
    # values being: [0, 0.15, 0.30, 0.45, 0.60, 0.75]
    #
    # cat colors contains the index of the value used in each
    # condition and category. It has shape 3x2 (condition by
    # category).
    hues = self.possible_hues[self.userps['catcolors']-1]

    # transpose it so category is indexed prior to condition (2x3)
    hues = np.transpose(hues)

    self.training = dict(
      lengths = scalefeatures(lengths),
      saturations = scalefeatures(saturations),
      hues = hues,
    )


  def _pandify(self):
    """
    convert array-based data to pandas
    """

    # start with generation
    generation = pd.DataFrame(
      columns = ['condition','stimulus','Hue','Saturation','Length']
    )
    for condition in range(3):
      exemplars = self.generation[:,:,condition]
      rows = pd.DataFrame(dict(
        condition = [self.conditions[condition]] * 6,
        stimulus = range(6),
        Length = exemplars[:,0].tolist(),
        Saturation = exemplars[:,1].tolist(),
        Hue = exemplars[:,2].tolist()
      ))
      # generation = generation.append(rows, ignore_index = True)
      generation = pd.concat([generation, pd.DataFrame(rows)], ignore_index = True)
    self.generation = generation

    # Now do training
    training = pd.DataFrame(
      columns = ['condition', 'category', 'stimulus', 'Hue','Saturation','Length']
    )
    for condition in range(3):
      for category in range(2):
        lengths = self.training['lengths'][:, category, condition]
        saturations = self.training['saturations'][:, category, condition]
        hue = self.training['hues'][category, condition]

        rows = pd.DataFrame(dict(
          condition = [self.conditions[condition]] * 4,
          category = [category] * 4,
          stimulus = range(4),
          Length = lengths.tolist(),
          Saturation = saturations.tolist(),
          Hue = hue.tolist()
        ))
        # training = training.append(rows, ignore_index = True)
        training = pd.concat([training, pd.DataFrame(rows)], ignore_index = True)
    self.training = training

  def stats(self):
    """
    Compute relevant generation statistics
    """

    ranges = pd.DataFrame(columns = ['condition'] + self.features)
    distances = pd.DataFrame(columns = ['condition','Within','Between'])

    for c, trainitems in self.training.groupby('condition'):
      A = self.getfeatures(trainitems)
      B = self.getfeatures(self.generation.loc[self.generation.condition==c])

      # compute ranges
      row = dict(zip(self.features,np.ptp(B,axis=0)))
      row['condition'] = c
      # ranges = ranges.append(row, ignore_index = True)
      ranges = pd.concat([ranges, pd.DataFrame([row])], ignore_index = True)

      # compute distances
      row = dict(condition = c)
      within_mat = Funcs.pdist(B, B)
      row['Within'] = np.mean(within_mat[np.triu(within_mat)>0])
      row['Between'] = np.mean(Funcs.pdist(A, B))
      # distances = distances.append(row, ignore_index = True)
      distances = pd.concat([distances, pd.DataFrame([row])], ignore_index = True)

    return dict(
      distances = distances,
      ranges = ranges
      )
