import sqlite3, sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

np.set_printoptions(precision = 2)
pd.set_option('display.precision', 2)
os.chdir(sys.path[0])

exec(compile(open('Imports.py', "rb").read(), 'Imports.py', 'exec'))
import Modules.Funcs as funcs

# import data
con = sqlite3.connect('../data/experiment.db')
info = pd.read_sql_query("SELECT * from participants", con)
df = pd.read_sql_query("SELECT * from generation", con)
stats = pd.read_sql_query("SELECT * from betastats", con)
stimuli = pd.read_sql_query("SELECT * from stimuli", con)
con.close()


stats = pd.merge(stats, info[['participant', 'condition']], on = 'participant')
df = pd.merge(df, info[['participant', 'condition']], on = 'participant')
df['y'] = stimuli.loc[df.stimulus, 'F2'].to_numpy()
df['x'] = stimuli.loc[df.stimulus, 'F1'].to_numpy()


print(stats[['condition','yrange']])

def plotlines(h, data, stats):
	sort_df = stats.sort_values(by = ['yrange','condition'])


	colors = ["#34495e", "#e74c3c"]
	condition_colors = dict(Middle = colors[1], Bottom = colors[0])
	n = 0

	for num, info in sort_df.iterrows():
		pid = info.participant
		g = info.condition

		rows = data.loc[data.participant == pid]

		# plot lines
		x = [n for i in range(2)]
		y = np.array([np.min(rows.y), np.max(rows.y)])
		h.plot(x, y, '-', alpha = 0.8,
			color = condition_colors[g])

		# plot examples
		x = [n for i in range(4)]
		y = np.array(rows.y)
		h.plot(x,y, '.', markersize = 4,
			fillstyle = 'full',
			markeredgecolor = condition_colors[g],
			color = condition_colors[g],
			alpha = 1)
		n += 1



	h.axis([-1.5, stats.shape[0] + 0.5,  -1.05, 1.05])
	h.set_yticks([])
	h.set_xticks([])
	h.set_ylabel('Y Axis Value', fontsize = 11)
	h.set_xlabel('Participant (sorted by overall range)', fontsize = 11)

	for k, v in condition_colors.items():
		plt.plot(np.NaN, np.NaN, '-', color = v, label = k)
	h.legend(loc="center left", fontsize = 11, frameon=False)


fh = plt.figure(figsize = (8,2))
plotlines(fh.gca(), df, stats)
[i.set_linewidth(1.0) for i in iter(fh.gca().spines.values())]


fh.savefig('yranges.pdf', bbox_inches = 'tight')
fh.savefig('yranges.png', bbox_inches = 'tight')
