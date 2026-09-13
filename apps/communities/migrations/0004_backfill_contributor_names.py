from django.db import migrations

def backfill(apps,schema_editor):
    Profile=apps.get_model('profiles','Profile')
    names=dict(Profile.objects.values_list('user_id','name'))
    for app,model,owner,field in [('communities','CommunityEvent','actor_id','actor_name'),('communities','SummaryResource','added_by_id','uploader_name'),('tasks','TaskFile','uploader_id','uploader_name'),('documents','DocumentVersion','uploader_id','uploader_name')]:
        Model=apps.get_model(app,model)
        for row in Model.objects.filter(**{field:''}).iterator():Model.objects.filter(pk=row.pk).update(**{field:names.get(getattr(row,owner),'Contributor #'+str(getattr(row,owner)))})
class Migration(migrations.Migration):
    dependencies=[('communities','0003_communityevent_actor_name_summaryresource_replaces_and_more'),('tasks','0002_taskfile_replaces_taskfile_revision_note_and_more'),('documents','0003_documentversion_uploader_name')]
    operations=[migrations.RunPython(backfill,migrations.RunPython.noop)]
