import sqlite3
# import enchant


from db_creation import database_create
from db_request import db_request_no_params, db_request_find_film, db_request_find_recommendations
from recommender import recommender


# d = enchant.Dict("en_US")


def input_check(word):

    word_check = d.check(word)
    if word_check is False:

        print 'Maybe your input is not correct:', word
        words_new = d.suggest(word)
        print 'Suggested input instead:'
        print words_new, 'Number of suggestions 1 -', len(words_new)
        num = raw_input('Please choose the word from the list, to continue search with the initial word input 0:  ')

        try:
            num=int(num)
        except:
            print 'Incorrect input, exit!'
            exit()

        if num > 0:
            suggest = words_new[num-1]
        else:
            suggest = word

        print 'Looking for:', suggest

    else:
        print 'Checking the input... done!'
        suggest = word

    return suggest


def genre_dict_empty(cur):

    genre_dict = dict()
    request_genre = db_request_no_params(cur, 'get genre')

    for item in request_genre:
        genre_dict[item[0]] = genre_dict.get(item[0], 0)
    return genre_dict


def print_result(search_result, genre_dict):

    id_local = None
    genres_out = dict()

    for item in search_result:

        genres_out[item[0]] = genres_out.get(item[0], '')+item[5]+' '
        genre_dict[item[4]] = genre_dict.get(item[4], 0)+1

        if int(item[0]) == id_local:
            continue

        print 'Film id:', item[0], '||', item[1], '|| Year:', item[2], '||  Rating:', item[3]

        id_local = int(item[0])

    print 'Genres for the film id:', genres_out


def main():

    conn = sqlite3.connect('movies.sqlite')
    conn.text_factory = str
    cur = conn.cursor()

    try:
        db_request_no_params(cur, 'get genre')
        print ('Database connected!')
    except:
        print 'Creating the database...'
        database_create(cur)

    conn.commit()

    # Input
    quest = raw_input('Please select the movie to find:')
    if len(quest) < 1:
        print 'Sorry, empty input'
        exit()

    # Checking the input
    # quest=input_check(quest)

    # Searching
    genre_dict = genre_dict_empty(cur)
    search_result = db_request_find_film(cur, quest)

    if len(search_result) < 1:
        print 'Your film is not in the database, sorry'
        exit()

    print_result(search_result, genre_dict)
    # print 'Genres dict after searching: ', genre_dict, '\n'  'Length:', len(genre_dict)

    print'\nCombined genre - based recommendations:\n'
    recommendation_results = recommender(quest, cur, genre_dict)

    for film in recommendation_results:
        recommended_films = db_request_find_recommendations(cur, film)
        print_result(recommended_films, genre_dict)

    # print 'Genres dict after recommendations: ', genre_dict, '\n'  'Length:', len(genre_dict)

    conn.close()

if __name__ == '__main__':
    main()
