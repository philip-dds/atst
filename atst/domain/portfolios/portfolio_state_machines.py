from atst.database import db

from .query import PortfoliosQuery

class PortfolioStateMachines(object):
    @classmethod
    def create(cls, user, portfolio_attrs):
        portfolio = PortfoliosQuery.create(**portfolio_attrs)
        perms_sets = PermissionSets.get_many(PortfolioRoles.PORTFOLIO_PERMISSION_SETS)
        Portfolios._create_portfolio_role(
            user,
            portfolio,
            status=PortfolioRoleStatus.ACTIVE,
            permission_sets=perms_sets,
        )
        PortfoliosQuery.add_and_commit(portfolio)
        return portfolio

    @classmethod
    def get(cls, user, portfolio_id):
        portfolio = PortfoliosQuery.get(portfolio_id)
        return ScopedPortfolio(user, portfolio)
