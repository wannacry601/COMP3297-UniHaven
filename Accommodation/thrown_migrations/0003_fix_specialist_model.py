from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('Accommodation', '0002_alter_house_bedrooms_alter_house_beds_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE Accommodation_specialist 
            ADD COLUMN specialist_user_id integer REFERENCES auth_user(id) ON DELETE CASCADE;
            ALTER TABLE Accommodation_specialist 
            ADD COLUMN email varchar(100) NOT NULL DEFAULT '';
            ALTER TABLE Accommodation_specialist 
            ADD COLUMN phone_number varchar(100) NOT NULL DEFAULT '';
            """,
            """
            ALTER TABLE Accommodation_specialist DROP COLUMN specialist_user_id;
            ALTER TABLE Accommodation_specialist DROP COLUMN email;
            ALTER TABLE Accommodation_specialist DROP COLUMN phone_number;
            """
        ),
    ]