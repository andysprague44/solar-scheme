from src import solar_scheme

if (__name__ == '__main__'):
    
    df = solar_scheme.run_solar_scheme()

    for index, row in df.iterrows():
        print([index] + row.tolist())
    
