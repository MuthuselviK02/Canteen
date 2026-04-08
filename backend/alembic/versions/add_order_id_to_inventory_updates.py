"""Add order_id to inventory_stock_updates table

Revision ID: add_order_id_to_inventory_updates
Revises: previous_migration
Create Date: 2026-02-06 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_order_id_to_inventory_updates'
down_revision = 'previous_migration'  # Replace with actual previous revision
branch_labels = None
depends_on = None

def upgrade():
    """Add order_id column to inventory_stock_updates table"""
    # Add order_id column as nullable to existing records
    op.add_column('inventory_stock_updates', sa.Column('order_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_inventory_stock_updates_order_id',
        'inventory_stock_updates', 
        'orders',
        ['order_id'], 
        ['id']
    )

def downgrade():
    """Remove order_id column from inventory_stock_updates table"""
    # Drop foreign key constraint
    op.drop_constraint('fk_inventory_stock_updates_order_id', 'inventory_stock_updates', type_='foreignkey')
    
    # Drop column
    op.drop_column('inventory_stock_updates', 'order_id')
