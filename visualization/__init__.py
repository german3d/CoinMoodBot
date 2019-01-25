import matplotlib as mpl
import platform

# Use another matplotlib backend on Mac OS
if platform.system() == "Darwin":
	mpl.use("TkAgg")
else:
	mpl.use("agg") # non-GUI backend
