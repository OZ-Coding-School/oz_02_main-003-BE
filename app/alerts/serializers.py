from rest_framework import serializers
from .models import Alert

class AlertSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    title = serializers.CharField(source='recipe.title') 
    
    def get_nickname(self, obj):
        return obj.user.nickname  
    
    class Meta:
        model = Alert
        fields = ['nickname', 'title', 'type', 'status', 'created_at']
