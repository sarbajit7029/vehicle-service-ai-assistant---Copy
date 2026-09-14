"""initial schema

Revision ID: 384a690176de
Revises: 
Create Date: 2026-09-13 23:27:27.023587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import VECTOR

# revision identifiers, used by Alembic.
revision: str = '384a690176de'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table('knowledge_documents',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('document_type', sa.String(length=20), nullable=False),
    sa.Column('file_path', sa.String(length=1000), nullable=False),
    sa.Column('status', sa.String(length=30), server_default='PENDING', nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("document_type IN ('PDF', 'DOCX', 'TXT', 'MARKDOWN')", name='ck_knowledge_documents_type'),
    sa.CheckConstraint("status IN ('PENDING', 'PROCESSING', 'INDEXED', 'FAILED', 'REJECTED')", name='ck_knowledge_documents_status'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_knowledge_documents_document_type', 'knowledge_documents', ['document_type'], unique=False)
    op.create_index('ix_knowledge_documents_status', 'knowledge_documents', ['status'], unique=False)
    op.create_table('service_types',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=True),
    sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('duration_minutes', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index('ix_service_types_name', 'service_types', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=30), server_default='CUSTOMER', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("role IN ('ADMIN', 'SERVICE_ADVISOR', 'TECHNICIAN', 'CUSTOMER')", name='ck_users_role'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    op.create_table('chat_sessions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'], unique=False)
    op.create_table('customers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('phone', sa.String(length=30), nullable=False),
    sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_customers_phone', 'customers', ['phone'], unique=False)
    op.create_table('knowledge_chunks',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('chunk_text', sa.Text(), nullable=False),
    sa.Column('page', sa.Integer(), nullable=True),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('embedding', VECTOR(), nullable=True),
    sa.ForeignKeyConstraint(['document_id'], ['knowledge_documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_knowledge_chunks_document_id', 'knowledge_chunks', ['document_id'], unique=False)
    op.create_index('ix_knowledge_chunks_page', 'knowledge_chunks', ['page'], unique=False)
    op.create_table('technicians',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('specialities', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_technicians_is_active', 'technicians', ['is_active'], unique=False)
    op.create_table('chat_messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chat_messages_created_at', 'chat_messages', ['created_at'], unique=False)
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'], unique=False)
    op.create_table('vehicles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('registration_no', sa.String(length=30), nullable=False),
    sa.Column('make', sa.String(length=100), nullable=False),
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('year', sa.SmallInteger(), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('registration_no')
    )
    op.create_index('ix_vehicles_customer_id', 'vehicles', ['customer_id'], unique=False)
    op.create_index('ix_vehicles_registration_no', 'vehicles', ['registration_no'], unique=False)
    op.create_table('service_bookings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('vehicle_id', sa.Integer(), nullable=False),
    sa.Column('service_type_id', sa.Integer(), nullable=False),
    sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=30), server_default='PENDING', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('PENDING', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')", name='ck_service_bookings_status'),
    sa.ForeignKeyConstraint(['service_type_id'], ['service_types.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_service_bookings_scheduled_at', 'service_bookings', ['scheduled_at'], unique=False)
    op.create_index('ix_service_bookings_status', 'service_bookings', ['status'], unique=False)
    op.create_index('ix_service_bookings_vehicle_id', 'service_bookings', ['vehicle_id'], unique=False)
    op.create_table('job_cards',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('booking_id', sa.Integer(), nullable=False),
    sa.Column('technician_id', sa.Integer(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('estimate', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
    sa.Column('status', sa.String(length=30), server_default='PENDING', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')", name='ck_job_cards_status'),
    sa.ForeignKeyConstraint(['booking_id'], ['service_bookings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['technician_id'], ['technicians.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id')
    )
    op.create_index('ix_job_cards_booking_id', 'job_cards', ['booking_id'], unique=False)
    op.create_index('ix_job_cards_status', 'job_cards', ['status'], unique=False)
    op.create_index('ix_job_cards_technician_id', 'job_cards', ['technician_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade database schema."""

    op.drop_index('ix_job_cards_technician_id', table_name='job_cards')
    op.drop_index('ix_job_cards_status', table_name='job_cards')
    op.drop_index('ix_job_cards_booking_id', table_name='job_cards')
    op.drop_table('job_cards')

    op.drop_index('ix_service_bookings_vehicle_id', table_name='service_bookings')
    op.drop_index('ix_service_bookings_status', table_name='service_bookings')
    op.drop_index('ix_service_bookings_scheduled_at', table_name='service_bookings')
    op.drop_table('service_bookings')

    op.drop_index('ix_vehicles_registration_no', table_name='vehicles')
    op.drop_index('ix_vehicles_customer_id', table_name='vehicles')
    op.drop_table('vehicles')

    op.drop_index('ix_chat_messages_session_id', table_name='chat_messages')
    op.drop_index('ix_chat_messages_created_at', table_name='chat_messages')
    op.drop_table('chat_messages')

    op.drop_index('ix_technicians_is_active', table_name='technicians')
    op.drop_table('technicians')

    op.drop_index('ix_knowledge_chunks_page', table_name='knowledge_chunks')
    op.drop_index('ix_knowledge_chunks_document_id', table_name='knowledge_chunks')
    op.drop_table('knowledge_chunks')

    op.drop_index('ix_customers_phone', table_name='customers')
    op.drop_table('customers')

    op.drop_index('ix_chat_sessions_user_id', table_name='chat_sessions')
    op.drop_table('chat_sessions')

    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index('ix_service_types_name', table_name='service_types')
    op.drop_table('service_types')

    op.drop_index('ix_knowledge_documents_status', table_name='knowledge_documents')
    op.drop_index('ix_knowledge_documents_document_type', table_name='knowledge_documents')
    op.drop_table('knowledge_documents')