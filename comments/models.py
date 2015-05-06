from django.db import models
from django.contrib.auth.models import User

from sql import cursor

from pastes.models import Paste

import datetime

class Comment(models.Model):
    COMMENTS_PER_PAGE = 10
    
    #paste = models.ForeignKey(Paste)
    #user = models.ForeignKey(User)
    
    text = models.TextField()
    
    submitted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    
    def get_comment():
        """
        Get a comment by its ID
        """
        query = """SELECT comments.id, paste_id, comments.user_id, auth_user.username AS username,
                          comments.text, submitted, edited FROM comments
                   INNER JOIN auth_user ON auth_user.id = comments.user_id
                   WHERE comments.id = %s"""
                   
        result = cursor.query_to_dict(query, [id])
        
        return result
    
    @staticmethod
    def add_comment(text, user, paste_id=None, char_id=None):
        """
        Add a comment
        """
        if char_id != None:
            paste_id = Paste.get_id(char_id)
        
        query = """INSERT INTO comments (paste_id, user_id, text, submitted)
                   VALUES ( %s, %s, %s, %s )"""
                   
        current_datetime = datetime.datetime.now()
                   
        cursor.query(query, [paste_id, user.id, text, current_datetime])
        
    @staticmethod
    def update_comment(text, id):
        """
        Update a comment
        """
        current_datetime = datetime.datetime.now()
        
        query = """UPDATE comments
                   SET text = %s, edited = %s
                   WHERE id = %s"""
                   
        cursor.query(query, [text, current_datetime, id])
        
    @staticmethod
    def delete_comment(id):
        """
        Delete a comment
        """
        query = """DELETE FROM comments
                   WHERE id = %s"""
                   
        cursor.query(query, [id])
    
    @staticmethod
    def get_comments(paste_id=None, char_id=None, offset=0, count=30, datetime_as_unix=False):
        """
        Get comments for a certain paste, starting from a provided offset
        
        If datetime_as_unix is True, datetimes will be converted to Unix timestamps. This is needed
        if the comment is going to be serialized into JSON.
        """
        if char_id != None:
            paste_id = Paste.get_id(char_id)
        
        query = """SELECT comments.id, paste_id, comments.user_id, auth_user.username AS username,
                          comments.text, submitted, edited FROM comments
                   INNER JOIN auth_user ON auth_user.id = comments.user_id
                   WHERE paste_id = %s
                   ORDER BY submitted DESC
                   OFFSET %s LIMIT %s"""
                   
        result = cursor.query_to_list(query, [paste_id, offset, count])
        
        if datetime_as_unix:
            for entry in result:
                entry["submitted"] = int(entry["submitted"].strftime("%s"))
                if entry["edited"] != None:
                    entry["edited"] = int(entry["edited"].strftime("%s"))
        
        return result
    
    @staticmethod
    def get_comment_count(paste_id=None, char_id=None):
        """
        Get amount of comments either. 
        If paste_id or char_id isn't provided, get the total amount of comments for all pastes
        """
        if char_id != None:
            paste_id = Paste.get_id(char_id)
        
        query = """SELECT COUNT(*) AS count FROM comments"""
        parameters = []
        
        if paste_id != None:
            query += "\nWHERE paste_id = %s"
            parameters.append(paste_id)
                   
        result = cursor.query_to_dict(query, parameters)
        
        return result["count"]