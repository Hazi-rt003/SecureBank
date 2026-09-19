"""add passkey and webauthn challenge tables

Revision ID: 331abc15cc39
Revises: c1f9992224ff
Create Date: 2026-09-09 13:10:24.148589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '331abc15cc39'
down_revision: Union[str, Sequence[str], None] = 'c1f9992224ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "passkey_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("credential_id", sa.String(), nullable=False),
        sa.Column("public_key", sa.LargeBinary(), nullable=False),
        sa.Column("sign_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("credential_id"),
    )

    op.create_index(
        op.f("ix_passkey_credentials_id"),
        "passkey_credentials",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_passkey_credentials_credential_id"),
        "passkey_credentials",
        ["credential_id"],
        unique=False,
    )

    op.create_table(
        "webauthn_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("challenge", sa.String(), nullable=False),
        sa.Column("purpose", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_webauthn_challenges_id"),
        "webauthn_challenges",
        ["id"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(
        op.f("ix_webauthn_challenges_id"),
        table_name="webauthn_challenges",
    )

    op.drop_table("webauthn_challenges")

    op.drop_index(
        op.f("ix_passkey_credentials_credential_id"),
        table_name="passkey_credentials",
    )

    op.drop_index(
        op.f("ix_passkey_credentials_id"),
        table_name="passkey_credentials",
    )

    op.drop_table("passkey_credentials")
    # ### end Alembic commands ###
