# core/serializers.py
from rest_framework import serializers
from .models import User, Company, UserCompanyMembership
from .models import User, Company, UserCompanyMembership, Permission, Role
from rest_framework import generics



class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'company_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        company_name = validated_data.pop('company_name')
        company, created = Company.objects.get_or_create(name=company_name)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        UserCompanyMembership.objects.create(user=user, company=company)
        
        return user

class UserSerializer(serializers.ModelSerializer):
    company_memberships = serializers.StringRelatedField(many=True, source='usercompanymembership_set')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'company_memberships']
        read_only_fields = ['is_active', 'date_joined']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'description']
        read_only_fields = ['id']

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=Permission.objects.all()
    )
    company = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'company', 'permissions']
        read_only_fields = ['id', 'company']

class UserCompanyMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    roles = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Role.objects.all()
    )

    class Meta:
        model = UserCompanyMembership
        fields = ['id', 'user', 'company', 'roles']
        read_only_fields = ['id', 'company']

    def validate(self, data):
        # Additional validation to ensure roles belong to the same company
        if 'roles' in data:
            user_company = self.context['request'].user.usercompanymembership_set.first().company
            for role in data['roles']:
                if role.company != user_company:
                    raise serializers.ValidationError("Roles must belong to the same company as the requesting user.")
        return data


# class CompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = ['id', 'name', 'is_active']

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     company_name = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'company_name']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         company_name = validated_data.pop('company_name')
        
#         # This is where we handle multi-tenancy upon registration
#         # Get or create the company. This is a common pattern for tenant creation.
#         company, created = Company.objects.get_or_create(name=company_name)
        
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
        
#         # Link the user to the company via the membership model
#         UserCompanyMembership.objects.create(user=user, company=company)
        
#         return user

# class UserSerializer(serializers.ModelSerializer):
#     # This serializer is for listing and retrieving user data
#     company_memberships = serializers.StringRelatedField(many=True, source='usercompanymembership_set')
    
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'company_memberships']
#         read_only_fields = ['is_active', 'date_joined']

# # core/serializers.py
# # ... (existing imports)

# class CompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = ['id', 'name', 'is_active', 'created_at']
#         read_only_fields = ['id', 'created_at']


# class RoleSerializer(serializers.ModelSerializer):
#     permissions = serializers.SlugRelatedField(
#         many=True,
#         slug_field='codename',
#         queryset=Permission.objects.all()
#     )
#     company = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = Role
#         fields = ['id', 'name', 'description', 'company', 'permissions']
#         read_only_fields = ['id', 'company']

# # core/serializers.py
# from rest_framework import serializers
# from .models import User, Company, UserCompanyMembership, Permission, Role
# # Note: Permission and Role were added to the import statement

# class CompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = ['id', 'name', 'is_active', 'created_at']
#         read_only_fields = ['id', 'created_at']

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     company_name = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'company_name']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         company_name = validated_data.pop('company_name')
        
#         company, created = Company.objects.get_or_create(name=company_name)
        
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
        
#         UserCompanyMembership.objects.create(user=user, company=company)
        
#         return user

# class UserSerializer(serializers.ModelSerializer):
#     company_memberships = serializers.StringRelatedField(many=True, source='usercompanymembership_set')
    
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'is_active', 'date_joined', 'company_memberships']
#         read_only_fields = ['is_active', 'date_joined']

# class PermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = ['id', 'codename', 'name', 'description']
#         read_only_fields = ['id']

# class RoleSerializer(serializers.ModelSerializer):
#     permissions = serializers.SlugRelatedField(
#         many=True,
#         slug_field='codename',
#         queryset=Permission.objects.all()
#     )
#     company = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = Role
#         fields = ['id', 'name', 'description', 'company', 'permissions']
#         read_only_fields = ['id', 'company']