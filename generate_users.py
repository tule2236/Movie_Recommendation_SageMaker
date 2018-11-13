'''generate fake user data'''
import random
import names as gen_name
import vars


def generate_users(count=vars.NUM_USERS):
    """ Create random users with gender and name """
    for _ in range(count):
        gender = random.choice(['female', 'male'])
        name = gen_name.get_full_name(gender=gender)
        user = {
            'gender': gender,
            'name': name,
        }
        yield user
