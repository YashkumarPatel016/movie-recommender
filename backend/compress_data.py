import pickle
import bz2

# 1. Load the original big files
print("Loading data...")
movies = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 2. Save them as compressed files (.pbz2)
print("Compressing files...")
pickle.dump(movies, bz2.open('movie_dict.pbz2', 'wb'))
pickle.dump(similarity, bz2.open('similarity.pbz2', 'wb'))

print("Done! You now have .pbz2 files. You can delete the .pkl files.")