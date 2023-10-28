# Libraries
from knox import crypto


def delete_other_tokens(*, request, new_token: str):
    digest = crypto.hash_token(new_token)
    request.user.auth_token_set.exclude(digest=digest).delete()
