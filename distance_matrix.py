import pandas as pd
from vincenty import vincenty
if __name__ == "__main__":
    df = pd.read_excel('stoppoint.xlsx') 
    distance_matrix = []
    
    # init distance matrix
    for i in df.index:
        row = []
        for j in df.index:
            row.append(vincenty([df['X'][i], df['Y'][i]], [df['X'][j], df['Y'][j]]))
        distance_matrix.append(row)
    
    distance_matrix_df = pd.DataFrame(distance_matrix)
    distance_matrix_df.to_excel("distance_matrix.xlsx")