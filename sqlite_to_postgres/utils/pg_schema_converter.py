import pandas as pd
import uuid
from copy import deepcopy

def df_to_pg(df):
    """
    Convert single table with all data from sqlite to several table ready to go to postgres
    :param df: dataframe with all data
    :return: splitted dataframes
    """

    # fix ids in the initial table
    df['id'] = [uuid.uuid4() for i in range(len(df))]

    # film_work table
    film_work = df[['id', 'title', 'plot', 'ratings', 'imdb_rating']]

    # genre table and its connecting table to films
    genre, film_work_genre = separate_table_genre('genre', df)

    # person table and its connecting table to films
    person, film_work_person = separate_table_person(['writers_names', 'actors_names', 'director'], 'name', df)

    return film_work, genre, person, film_work_genre, film_work_person


def separate_table_genre(name, df):
    """
    separates genre into table with genres and connecting table
    :param name: str, name of a column to be separated
    :param df: dataframe with all data
    :return: 2 dataframes
    """
    # explode table, by separating each genre (currently one film can have a list of genres: comedy, horror)
    df_interm_full = pd.concat([pd.DataFrame(data={'id': row['id'], name: row[name].split(', ')})
                            for _, row in df.iterrows()]).reset_index(drop=True)

    # find unique genres and give them ids
    df_interm_selected = deepcopy(df_interm_full)[[name]].drop_duplicates(ignore_index=True).dropna()
    df_interm_selected[f'{name}_id'] = [uuid.uuid4() for i in range(len(df_interm_selected))]

    # join full table with genres id
    df_interm_full = df_interm_full.merge(df_interm_selected, on=name, how='left')

    # finally change names to correspond to schema
    df_connecting = df_interm_full[['id', f'{name}_id']].dropna()
    df_connecting = df_connecting.rename(columns={'id': 'movie_id'})
    df_interm_selected = df_interm_selected.rename(columns={name: 'name', f'{name}_id': 'id'})

    return df_interm_selected, df_connecting


def separate_table_person(names, new_col, df):
    """
    separates data into dataframe with persons and connecting table
    :param names: list of str, columns which should be separated
    :param new_col: str, new column name
    :param df: dataframe with all data
    :return: 2 dataframes
    """
    names_id = deepcopy(names)
    names_id.extend(['id'])

    # explode table, by separating each person in each column (currently one film can have a list of persons,
    # e.g. writes_names: name1, name2)
    df_interm_full = []
    for name in names:
        role = name.split('_')[0]
        role = role[:-1] if role[-1] == 's' else role

        for _, row in df.iterrows():
            if row[name] is not None:
                new_col_val = row[name].split(', ')
                ids = [row['id']] * len(new_col_val)
                roles = [role] * len(new_col_val)
                if len(new_col_val) == 1:
                    df_interm_full.append(pd.DataFrame(data={'id': ids, 'role': roles, new_col: new_col_val}, index=[0]))
                else:
                    df_interm_full.append(pd.DataFrame(data={'id': ids, 'role': roles, new_col: new_col_val}))

    df_interm_full = pd.concat(df_interm_full).reset_index(drop=True)

    # find unique genres and give them ids
    df_interm_selected = deepcopy(df_interm_full)[[new_col, 'role']].drop_duplicates(ignore_index=True).dropna()
    df_interm_selected['person_id'] = [uuid.uuid4() for i in range(len(df_interm_selected))]

    # join full table with genres id
    df_interm_full = df_interm_full.merge(df_interm_selected, on=[new_col, 'role'], how='left')

    # finally change names to correspond to schema
    df_connecting = df_interm_full[['id', 'person_id']].dropna()
    df_connecting = df_connecting.rename(columns={'id': 'movie_id'})
    df_interm_selected = df_interm_selected.rename(columns={'person_id': 'id'})

    return df_interm_selected, df_connecting

