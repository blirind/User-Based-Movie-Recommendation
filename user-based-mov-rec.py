

def create_5_rec():

    # Importing pandas library and setting maximum displayable column number to 20:
    import pandas as pd
    pd.set_option('display.max_columns', 20)

    # Importing the datasets and merging them in one dataframe:
    movie = pd.read_csv('Bootcamp/Week4/Ders Oncesi Notlar/movie_lens_dataset/movie.csv')
    rating = pd.read_csv('Bootcamp/Week4/Ders Oncesi Notlar/movie_lens_dataset/rating.csv')
    df = movie.merge(rating, how="left", on="movieId")

    # Creating a new dataframe called comment_counts to see the number of ratings per movie:
    comment_counts = pd.DataFrame(df["title"].value_counts())

    # Saving movie indexes which have 5000 or less rating in a new dataframe called rare_movies:
    rare_movies = comment_counts[comment_counts["title"] <= 5000].index

    # Eliminating rare_movies from our original df and saving as common_movies.
    # So common_movies dataframe now hold the movies with higher than 5000 rating per movie:
    common_movies = df[~df["title"].isin(rare_movies)]

    # Creating the user_movie_df dataframe as a pivot table. This table will hold the information of
    # userid's rating per movie title:
    user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

    # Choosing a random user from user_movie_df:
    random_user = int(pd.Series(user_movie_df.index).sample(1, random_state=33).values)

    # Selecting the random_user and all the movies (some of them are watched and rated by this user):
    random_user_df = user_movie_df[user_movie_df.index == random_user]

    # Getting as a list only the columns of random_user_df dataframe which are filled with rating
    # scores. So movies_watched is the list of movies our random_user watched and rated:
    movies_watched = random_user_df.columns[random_user_df.notna().any()].tolist()

    # From user_movie_df, extracting the movies_watched by random_user, and the scores of them
    # for each user in user_movie_df. Actually bringing "potential friends" of our random_user:
    movies_watched_df = user_movie_df[movies_watched]

    # Getting the number of same movies each user watched with random_user:
    user_movie_count = movies_watched_df.T.notnull().sum().reset_index()

    # Setting new column names of user_movie_count dataframe:
    user_movie_count.columns = ["userId", "movie_count"]

    # Setting a threshold of watched the same movies between all users and random_user.
    watched_movie_th = (user_movie_count["movie_count"].max()) * 80 / 100

    # Selecting each user if it watched %80 of movies our random_user watched:
    users_same_movies = user_movie_count[user_movie_count["movie_count"] > watched_movie_th]["userId"]

    # Merging the indexes of users_same_movies and watched_movies of random_user_df.
    final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(users_same_movies)],random_user_df[movies_watched]])

    # Getting the correlation rates between users, dropping duplicates:
    corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()

    # Turning corr_df to dataframe with a column named "corr":
    corr_df = pd.DataFrame(corr_df, columns=["corr"])

    # Naming corr_df indexes as user_id_1 and user_id_2 and setting a new index no:
    corr_df.index.names = ['user_id_1', 'user_id_2']
    corr_df = corr_df.reset_index()

    # Getting top_users dataframe. It contains the information of only random_user from user_id_1
    # and if the correlation rate is higher than 0.62; while bringing the user_id_2 index and
    # it's correlation rate.
    top_users = corr_df[(corr_df["user_id_1"] == random_user) & (corr_df["corr"] >= 0.62)][
        ["user_id_2", "corr"]].reset_index(drop=True)

    # Sorting values by corr column by descending:
    top_users = top_users.sort_values(by='corr', ascending=False)

    # Renaming columns of top_users dataframe:
    top_users.rename(columns={"user_id_2": "userId"}, inplace=True)

    # Creating a new dataframe called top_users_ratings by merging top_users dataframe and
    # the "userId", "movieId" and "rating" columns of rating dataframe with inner method:
    top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')

    # Eliminating random_user from the dataframe to get only "potential friends" correlation
    top_users_ratings = top_users_ratings[top_users_ratings["userId"] != random_user]

    # Creating a new column called "weighted_rating" by multiplying "corr" with "rating" columns:
    top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']

    # Getting the mean of weighted_rating by movieId and reseting index:
    recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
    recommendation_df = recommendation_df.reset_index()

    # Getting 5 potentially most favorite movies for our random_user:
    movies_to_be_recommend = recommendation_df.sort_values("weighted_rating", ascending=False).head(5)

    # Saving only the names of the movies to the final_recommendation:
    final_recommendation = movies_to_be_recommend.merge(movie[["movieId", "title"]])["title"]

    # returning the result:
    return final_recommendation

create_5_rec()