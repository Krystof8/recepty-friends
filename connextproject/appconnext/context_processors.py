from .models import FriendsRequestModel, FriendListModel

def friend_request_count(request):
    count = 0
    if request.user.is_authenticated:
        count = FriendsRequestModel.objects.filter(request_receiver=request.user.username).count()
    return {
        'pending_friend_requests': count
    }