#=============================================================================================================================#
#                                                        MarketPulse
#  Indian Financial News Aggregator — Moneycontrol.com & NDTVProfit.com
#=============================================================================================================================#

from MarketPulse import Moneycontrol, NdtvProfit, MarketPulseConfig
from rich.console import Console

# #--------------------------------------------------- Configuration Section ----------------------------------------------------

# # GLOBAL SETTINGS (Affects all new instances by default)
# MarketPulseConfig.max_rps      = 2.0    # Default: 2.0  (requests per second)
# MarketPulseConfig.retries      = 3      # Default: 3
# MarketPulseConfig.retry_delay  = 2.0    # Default: 2.0
# MarketPulseConfig.cookie_cache = True   # Default: True

# #--------------------------------------------------- Initialize Clients ----------------------------------------------------

mc   = Moneycontrol()
ndtv = NdtvProfit()
rich = Console()


# #==========================================================================================================================#
# #                                           MONEYCONTROL NEWS
# #==========================================================================================================================#

# #---------------------------------------------------------- Latest News ----------------------------------------------------------

# # 🔹 Latest News
# print(mc.latest_news())                                                       # Latest 25 news articles (DataFrame)
# print(mc.latest_news(limit=10))                                               # Latest 10 articles
# print(mc.latest_news(output="json"))                                          # JSON output

# #---------------------------------------------------------- Market News ----------------------------------------------------------

# # 🔹 Market News
# print(mc.market_news())                                                       # Market-specific news
# print(mc.market_news(limit=10))                                               # Top 10 market articles

# #---------------------------------------------------------- Economy News ----------------------------------------------------------

# # 🔹 Economy & Macro News
# print(mc.economy_news())                                                      # Economy updates, GDP, RBI

# #---------------------------------------------------------- IPO News ----------------------------------------------------------

# # 🔹 IPO News
# print(mc.ipo_news())                                                          # IPO listings, subscriptions
# print(mc.ipo_news(limit=5))                                                   # Top 5 IPO articles

# #---------------------------------------------------------- Expert Opinions ----------------------------------------------------------

# # 🔹 Expert Views & Analysis
# print(mc.expert_opinions())                                                   # Expert opinions & analysis

# #---------------------------------------------------------- Personal Finance ----------------------------------------------------------

# # 🔹 Personal Finance
# print(mc.personal_finance())                                                  # Tax, savings, insurance

# #---------------------------------------------------------- Mutual Funds ----------------------------------------------------------

# # 🔹 Mutual Funds News
# print(mc.mutual_funds_news())                                                 # Mutual fund updates

# #---------------------------------------------------------- Stock-Specific News ----------------------------------------------------------

# # 🔹 Stock-Specific News
# print(mc.stock_news("reliance"))                                              # News for Reliance
# print(mc.stock_news("tcs", limit=5))                                         # Top 5 TCS news
# print(mc.stock_news("hdfc-bank"))                                             # HDFC Bank news

# #---------------------------------------------------------- Trending News ----------------------------------------------------------

# # 🔹 Trending Stories
# print(mc.trending_news())                                                     # Currently trending stories

# #---------------------------------------------------------- Full Article ----------------------------------------------------------

# # 🔹 Full Article Content
# detail = mc.article_detail("https://www.moneycontrol.com/news/business/...")   # Full article text
# print(detail["title"])
# print(detail["summary"])
# print(detail["content"][:500])                                                # First 500 chars


# #==========================================================================================================================#
# #                                           NDTV PROFIT NEWS
# #==========================================================================================================================#

# #---------------------------------------------------------- Latest News ----------------------------------------------------------

# # 🔹 Latest News
# print(ndtv.latest_news())                                                     # Latest 25 news articles
# print(ndtv.latest_news(limit=10))                                             # Latest 10 articles
# print(ndtv.latest_news(output="json"))                                        # JSON output

# #---------------------------------------------------------- Market News ----------------------------------------------------------

# # 🔹 Market News
# print(ndtv.market_news())                                                     # Markets section news
# print(ndtv.market_news(limit=10))                                             # Top 10 market articles

# #---------------------------------------------------------- Economy News ----------------------------------------------------------

# # 🔹 Economy & Policy News
# print(ndtv.economy_news())                                                    # Economy, RBI, fiscal policy

# #---------------------------------------------------------- Opinion & Analysis ----------------------------------------------------------

# # 🔹 Opinion Articles
# print(ndtv.opinion_news())                                                    # Editorials, expert columns

# #---------------------------------------------------------- Technology News ----------------------------------------------------------

# # 🔹 Technology News
# print(ndtv.technology_news())                                                 # Tech stocks, startups

# #---------------------------------------------------------- Stock-Specific News ----------------------------------------------------------

# # 🔹 Stock-Specific News
# print(ndtv.stock_news("reliance"))                                            # News for Reliance
# print(ndtv.stock_news("infosys", limit=5))                                    # Top 5 Infosys news

# #---------------------------------------------------------- Trending News ----------------------------------------------------------

# # 🔹 Trending Stories
# print(ndtv.trending_news())                                                   # Trending from homepage

# #---------------------------------------------------------- Full Article ----------------------------------------------------------

# # 🔹 Full Article Content
# detail = ndtv.article_detail("https://www.ndtvprofit.com/markets/...")         # Full article text
# print(detail["title"])
# print(detail["summary"])
# print(detail["content"][:500])


# #==========================================================================================================================#
# #                                           CROSS-SOURCE (Combined)
# #==========================================================================================================================#

# # 🔹 Combined Latest from Both Sources
# mc_latest   = mc.latest_news(limit=10, output="json")
# ndtv_latest = ndtv.latest_news(limit=10, output="json")
# all_news    = mc_latest + ndtv_latest
# rich.print(f"Total articles: {len(all_news)}")

# # 🔹 Combined Stock News
# mc_rel   = mc.stock_news("reliance", limit=5, output="json")
# ndtv_rel = ndtv.stock_news("reliance", limit=5, output="json")
# all_rel  = mc_rel + ndtv_rel
# for article in all_rel:
#     print(f"[{article['source']}] {article['title']}")
