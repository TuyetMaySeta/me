"""
Migration script to rename CV tables and columns to Employee
Run with: python migrate.py generate "Rename CV to Employee tables"
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'rename_cv_to_employee'
down_revision = 'a5ce4db5fb27'  # Previous migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Rename CV tables and columns to Employee"""
    
    # 1. Rename main table: cv → employee
    op.rename_table('cv', 'employee')
    
    # 2. Rename id_seta column to employee_id in employee table
    # Note: id_seta was the business identifier, now it becomes employee_id
    # The technical ID (6-char) remains as 'id'
    with op.batch_alter_table('employee') as batch_op:
        batch_op.alter_column('id_seta', new_column_name='employee_id')
    
    # 3. Rename related tables and update foreign key columns
    
    # Languages: cv_id → employee_id
    op.rename_table('languages', 'employee_languages')
    with op.batch_alter_table('employee_languages') as batch_op:
        batch_op.alter_column('cv_id', new_column_name='employee_id')
    
    # Technical Skills: cv_id → employee_id  
    op.rename_table('technical_skills', 'employee_technical_skills')
    with op.batch_alter_table('employee_technical_skills') as batch_op:
        batch_op.alter_column('cv_id', new_column_name='employee_id')
    
    # Soft Skills: cv_id → employee_id
    op.rename_table('soft_skills', 'employee_soft_skills')
    with op.batch_alter_table('employee_soft_skills') as batch_op:
        batch_op.alter_column('cv_id', new_column_name='employee_id')
    
    # Projects: cv_id → employee_id
    op.rename_table('projects', 'employee_projects')
    with op.batch_alter_table('employee_projects') as batch_op:
        batch_op.alter_column('cv_id', new_column_name='employee_id')
    
    # 4. Rename draft tables
    
    # CV Draft: id_seta → employee_id
    op.rename_table('cv_draft', 'employee_draft')
    with op.batch_alter_table('employee_draft') as batch_op:
        batch_op.alter_column('id_seta', new_column_name='employee_id')
    
    # Language Drafts: draft_id remains same (references employee_draft.id)
    op.rename_table('language_drafts', 'employee_language_drafts')
    
    # Technical Skill Drafts: draft_id remains same
    op.rename_table('technical_skill_drafts', 'employee_technical_skill_drafts')
    
    # Soft Skill Drafts: draft_id remains same  
    op.rename_table('soft_skill_drafts', 'employee_soft_skill_drafts')
    
    # Project Drafts: draft_id remains same
    op.rename_table('project_drafts', 'employee_project_drafts')
    
    # 5. Update indexes (PostgreSQL automatically renames most indexes)
    # But we need to rename the email index
    op.drop_index('ix_cv_email', 'employee')
    op.create_index('ix_employee_email', 'employee', ['email'])
    
    # Draft email index
    op.drop_index('ix_cv_draft_email', 'employee_draft')  
    op.create_index('ix_employee_draft_email', 'employee_draft', ['email'])


def downgrade() -> None:
    """Revert Employee tables back to CV"""
    
    # Reverse all the operations in opposite order
    
    # 1. Revert indexes
    op.drop_index('ix_employee_draft_email', 'employee_draft')
    op.create_index('ix_cv_draft_email', 'employee_draft', ['email'])
    
    op.drop_index('ix_employee_email', 'employee')
    op.create_index('ix_cv_email', 'employee', ['email'])
    
    # 2. Revert draft tables
    op.rename_table('employee_project_drafts', 'project_drafts')
    op.rename_table('employee_soft_skill_drafts', 'soft_skill_drafts')
    op.rename_table('employee_technical_skill_drafts', 'technical_skill_drafts')
    op.rename_table('employee_language_drafts', 'language_drafts')
    
    with op.batch_alter_table('employee_draft') as batch_op:
        batch_op.alter_column('employee_id', new_column_name='id_seta')
    op.rename_table('employee_draft', 'cv_draft')
    
    # 3. Revert related tables
    with op.batch_alter_table('employee_projects') as batch_op:
        batch_op.alter_column('employee_id', new_column_name='cv_id')
    op.rename_table('employee_projects', 'projects')
    
    with op.batch_alter_table('employee_soft_skills') as batch_op:
        batch_op.alter_column('employee_id', new_column_name='cv_id')
    op.rename_table('employee_soft_skills', 'soft_skills')
    
    with op.batch_alter_table('employee_technical_skills') as batch_op:
        batch_op.alter_column('employee_id', new_column_name='cv_id')
    op.rename_table('employee_technical_skills', 'technical_skills')
    
    with op.batch_alter_table('employee_languages') as batch_op:
        batch_op.alter_column('employee_id', new_column_name='cv_id')
    op.rename_table('employee_languages', 'languages')
    
    # 4. Revert main table
    with op.batch_alter_table('employee') as batch_op:
        batch_op.alter_column('employee_id', new_column_name='id_seta')
    op.rename_table('employee', 'cv')
