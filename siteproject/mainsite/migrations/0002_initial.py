# Generated by Django 5.1.2 on 2025-01-19 20:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mainsite', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='commentmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentsvotemodel',
            name='content',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainsite.commentmodel'),
        ),
        migrations.AddField(
            model_name='commentsvotemodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedback',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playlistmodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playlist_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='playlistmodel',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlist_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postsmodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts_author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postsvotemodel',
            name='content',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts_votes', to='mainsite.postsmodel'),
        ),
        migrations.AddField(
            model_name='postsvotemodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='searchrequests',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscribemodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscribemodel',
            name='subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userviewmodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='videomodel',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userviewmodel',
            name='video',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='mainsite.videomodel'),
        ),
        migrations.AddField(
            model_name='pagevisit',
            name='video',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainsite.videomodel'),
        ),
        migrations.AddField(
            model_name='videoplaylistmodel',
            name='playlist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_playlists', to='mainsite.playlistmodel'),
        ),
        migrations.AddField(
            model_name='videoplaylistmodel',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_playlists', to='mainsite.videomodel'),
        ),
        migrations.AddField(
            model_name='votemodel',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_votes', to='mainsite.videomodel'),
        ),
        migrations.AddField(
            model_name='votemodel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='subscribemodel',
            unique_together={('author', 'subscriber')},
        ),
        migrations.AlterUniqueTogether(
            name='pagevisit',
            unique_together={('user', 'video')},
        ),
        migrations.AlterUniqueTogether(
            name='videoplaylistmodel',
            unique_together={('video', 'playlist')},
        ),
    ]
