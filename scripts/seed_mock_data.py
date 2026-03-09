#!/usr/bin/env python3
"""
Generate mock feedback and messages data for the llm-annotator database.

Theme: Personal finance & small business accounting - scenarios where the LLM
gave flawed, outdated, or unhelpful advice, leading to user dissatisfaction.

Upload: make seed DB_NAME=llm_annotator
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    psycopg2 = None

# Model manifest from configs/config.yaml (lines 5-9)
MODEL_MANIFEST = {
    "name": "gemini-flash",
    "model": "gemini/gemini-2.5-flash",
    "temperature": 0,
    "max_tokens": 1024,
}


@dataclass
class Data:
    messages: list[dict[str, Any]]
    feedback: str
    model_manifest: dict[str, Any]


# Each message: {"role": "user"|"assistant", "content": str}
# model_manifest on assistant messages comes from Data.model_manifest
Datas: list[Data] = [
    Data(
        messages=[
            {"role": "user", "content": "What is the deadline for filing 2024 US federal tax return?"},
            {"role": "assistant", "content": "The deadline for 2024 federal tax returns is April 15, 2025. You have plenty of time!"},
            {"role": "user", "content": "What if I need an extension?"},
            {"role": "assistant", "content": "You can file Form 4868 for an automatic 6-month extension. But I think the form number might have changed."},
        ],
        feedback="The information was wrong - I checked the IRS website and the deadline is different.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "I run a sole proprietorship. When do I need to pay estimated quarterly taxes?"},
            {"role": "assistant", "content": "You need to pay estimated taxes on the 15th of January, April, June, and September. Actually wait, I think it might be different for some states."},
        ],
        feedback="Contradictory advice - first said one thing, then said to verify elsewhere.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Can I deduct my home office if I work from home 3 days a week?"},
            {"role": "assistant", "content": "Yes, you can deduct a portion of your rent or mortgage. The IRS allows up to $5 per square foot for the home office deduction."},
        ],
        feedback="The deduction amount was wrong. Double-checked with my CPA.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What records do I need to keep for business expense deductions?"},
            {"role": "assistant", "content": "Generally you should keep receipts for 3 years. For asset purchases like equipment, keep records for 7 years."},
        ],
        feedback="Said to keep records 3 years but audit can go back 6 years.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Is there a standard deduction for self-employed people?"},
            {"role": "assistant", "content": "Self-employed individuals use the same standard deduction as employees. For 2024 it is $14,600 for single filers."},
        ],
        feedback="The standard deduction amount was wrong for 2024.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the 2024 401k contribution limit?"},
            {"role": "assistant", "content": "The 2024 401(k) contribution limit is $23,000 for employees under 50, and $30,500 for those 50 and older with catch-up contributions."},
        ],
        feedback="The catch-up contribution amount was incorrect.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How much can I contribute to an IRA if I have a 401k?"},
            {"role": "assistant", "content": "If you have a 401(k), you can still contribute up to $7,000 to a traditional IRA in 2024. The deduction may be limited based on income."},
        ],
        feedback="The income threshold for IRA deduction was incorrect.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the current federal minimum wage?"},
            {"role": "assistant", "content": "The federal minimum wage is $7.25 per hour. Many states have higher minimum wages, so check your state laws."},
        ],
        feedback="Gave me outdated figures. Very frustrating.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "台股除權息要怎麼報稅？"},
            {"role": "assistant", "content": "除權息所得要併入綜合所得稅。股利可抵減稅額約 8.5%，但上限 8 萬元。不過每年規定可能調整，建議再確認一下。"},
        ],
        feedback="台股除權息的稅制講錯了，害我差點報錯。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "美股股息會被扣 30% 預扣稅嗎？"},
            {"role": "assistant", "content": "非美國居民的美股股息通常扣 30%。若台灣與美國有租稅協定，可能可降至 15%。但協定細節我記不太清楚，你最好問會計師。"},
        ],
        feedback="美股預扣稅的協定細節完全搞混。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "技術分析裡的 MACD 金叉死叉怎麼看？"},
            {"role": "assistant", "content": "MACD 線穿越訊號線時產生金叉（買入）或死叉（賣出）。一般看 DIF 和 DEA，但參數設定每家不同，我沒辦法給你具體數字。"},
        ],
        feedback="回答太模糊，一直說「建議諮詢專業人士」根本沒幫到忙。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "加密貨幣的損益要報稅嗎？"},
            {"role": "assistant", "content": "台灣目前將加密貨幣視為財產，交易所得要申報。但具體怎麼算、用哪個稅目，法規還在變，建議諮詢專業人士。"},
        ],
        feedback="資訊有誤，我查了官網發現不一樣。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "基本面分析要看哪些財務指標？"},
            {"role": "assistant", "content": "常見的有本益比、ROE、負債比、營收成長率等。每個產業重點不同，很難一概而論。"},
        ],
        feedback="This answer was too vague. I needed specific numbers, not 'it depends'.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "公司要開發票給個人，統編可以留空嗎？"},
            {"role": "assistant", "content": "若買方是個人且不需要報帳，統編可留空。但 B2B 的話通常要填，詳細規定可能因行業而異。"},
        ],
        feedback="Did not address my actual question. Gave generic textbook answer.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "季報和年報的申報期限各是什麼時候？"},
            {"role": "assistant", "content": "上市櫃公司季報是每季結束後 45 天內，年報是 3 月底前。非公開發行公司可能不同，我對這塊不太確定。"},
        ],
        feedback="Kept saying 'consult a professional' - I was hoping for at least a starting point.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "美股和台股的交易時間差幾小時？"},
            {"role": "assistant", "content": "台股是 9:00–13:30，美股是美東 9:30–16:00。換算成台灣時間會因夏令時間而變，我沒法給你精確換算。"},
        ],
        feedback="沒給具體換算，只說會因夏令時間而變。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "K 線的紅棒綠棒在美股和台股代表的意思一樣嗎？"},
            {"role": "assistant", "content": "台股紅漲綠跌，美股相反是綠漲紅跌。但有些軟體可以自訂顏色，所以還是要看你的設定。"},
        ],
        feedback="搞混了，我用的券商介面跟它說的不一樣。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "營所稅的暫繳申報是什麼時候？"},
            {"role": "assistant", "content": "營利事業要在 9 月 1 日到 9 月 30 日辦理暫繳。但符合一定條件可以免辦，詳細規定要查一下。"},
        ],
        feedback="暫繳的免辦條件講錯了，害我白跑一趟。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "勞健保的級距怎麼算？我是負責人只有我一人。"},
            {"role": "assistant", "content": "負責人勞保可以自願加保，健保則依投保金額級距。最低投保金額約 25,250，但每年會調整。"},
        ],
        feedback="級距金額是錯的，我查了勞保局網站。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "二代健保補充保費的門檻是多少？"},
            {"role": "assistant", "content": "單次給付超過 2 萬元要扣 2.11% 補充保費。但股利、利息、租金等有不同計算方式，建議看健保署說明。"},
        ],
        feedback="補充保費的費率講錯了，已經有調整過。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "綜合所得稅的列舉扣除有哪些？"},
            {"role": "assistant", "content": "常見的有捐贈、保險費、醫藥費、房貸利息等。每人每年有不同上限，標準扣除額和列舉只能擇一。"},
        ],
        feedback="捐贈扣除的上限金額不對。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "營業稅的零稅率跟免稅差在哪？"},
            {"role": "assistant", "content": "零稅率可以退進項稅額，免稅則不行。外銷通常適用零稅率，但要看具體貨物或勞務類型。"},
        ],
        feedback="舉的例子不適用我的行業，回答太籠統。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "存股族領股利要繳多少稅？"},
            {"role": "assistant", "content": "股利可選合併計稅或分開計稅。合併的話有 8.5% 可抵減，上限 8 萬；分開計稅 28%。哪個划算要看你的所得級距。"},
        ],
        feedback="可抵減的百分比說錯了，我對過國稅局試算。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "RSI 超買超賣的區間一般是多少？"},
            {"role": "assistant", "content": "通常 RSI 超過 70 算超買，低於 30 算超賣。但 14 日是最常用參數，不同週期可能不一樣。"},
        ],
        feedback="參數預設值講得含糊，我用的軟體預設不是 14。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "有限公司跟股份有限公司的差別？"},
            {"role": "assistant", "content": "有限公司股東 1-50 人，股份有限則無上限。責任都是有限，但組織架構、股權轉讓規定不同。設立時要選對類型。"},
        ],
        feedback="股東人數上限講錯了，公司法有修過。",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What percentage should I withhold for self-employment tax?"},
            {"role": "assistant", "content": "Self-employment tax is approximately 15.3% on your net profit. You should also set aside money for income tax, so aim for 25-30% total."},
        ],
        feedback="The numbers were incorrect. I could have gotten in trouble with the IRS.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the small business health care tax credit threshold?"},
            {"role": "assistant", "content": "The credit is available to businesses with fewer than 25 full-time equivalent employees and average wages under $50,000. The exact percentage varies."},
        ],
        feedback="Too many caveats and 'may' - I needed a clear answer.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I calculate depreciation for my business laptop?"},
            {"role": "assistant", "content": "You can depreciate it over several years using MACRS. The exact method depends on the asset class. Consult a tax professional for details."},
            {"role": "user", "content": "The laptop cost $1,200. What is the first year deduction?"},
            {"role": "assistant", "content": "Under 5-year property, you might get around $240 in year one. But the convention (half-year vs mid-quarter) affects this."},
        ],
        feedback="The depreciation method was wrong for my asset class.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Should I use cash or accrual accounting for my small business?"},
            {"role": "assistant", "content": "It depends on your business type and size. Cash basis is simpler; accrual gives a more accurate picture. Consider your needs."},
        ],
        feedback="This answer was too vague. I needed specific numbers, not 'it depends'.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle sales tax for online sales across different states?"},
            {"role": "assistant", "content": "Nexus rules vary by state. Generally you need to collect sales tax where you have physical presence or economic nexus. Each state has different thresholds."},
        ],
        feedback="Did not understand my question about nexus. Gave irrelevant answer.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the difference between W-2 and 1099 for contractors?"},
            {"role": "assistant", "content": "W-2 employees have taxes withheld; 1099 contractors are responsible for their own taxes. Misclassification can lead to penalties. The IRS uses a 20-factor test."},
        ],
        feedback="Mixed up 1099-NEC and 1099-MISC. Not reliable for tax questions.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Can I write off my car for business use?"},
            {"role": "assistant", "content": "Yes, you can use either the standard mileage rate or actual expenses. You need to track business vs personal miles. The rate changes annually."},
        ],
        feedback="The mileage rate was wrong. It changed in 2024.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Do I need to issue 1099s to my subcontractors?"},
            {"role": "assistant", "content": "You need to issue 1099-NEC to unincorporated contractors you pay $600 or more. Corporations are generally exempt, but S-corps might not be. Check the instructions."},
            {"role": "user", "content": "What about an LLC that elected S-corp status?"},
            {"role": "assistant", "content": "S-corps are typically exempt from 1099-NEC. But single-member LLCs might still need one."},
            {"role": "user", "content": "And when is the deadline to send them?"},
            {"role": "assistant", "content": "January 31 for both the recipient and IRS copy. But there was a recent extension - I would verify."},
        ],
        feedback="Said corporations are exempt from 1099 but that is not always true.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I value inventory for tax purposes?"},
            {"role": "assistant", "content": "You can use FIFO, LIFO, or specific identification. Once you choose a method, you generally need to stick with it. LIFO has special rules."},
        ],
        feedback="Too much jargon. I am not an accountant - need plain English.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What qualifies as a Section 179 deduction?"},
            {"role": "assistant", "content": "Section 179 allows immediate expensing of certain business property. There are limits that change each year. Equipment and software often qualify."},
        ],
        feedback="The Section 179 limit was outdated. Useless for planning.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "When do I need to register for an EIN?"},
            {"role": "assistant", "content": "You need an EIN if you have employees, operate as a corporation or partnership, or have a Keogh plan. Sole proprietors can use their SSN for some purposes."},
        ],
        feedback="The EIN requirement was wrong for sole proprietors.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle foreign currency gains in my business?"},
            {"role": "assistant", "content": "Foreign currency transactions are generally translated at the exchange rate on the transaction date. Gains and losses go on Schedule C or Form 988. It gets complex."},
        ],
        feedback="Said 'consult your accountant' three times. I am trying to avoid that cost.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the penalty for late payroll tax deposit?"},
            {"role": "assistant", "content": "The penalty is 2% if you are 1-5 days late, 5% if 6-15 days, and 10% after 15 days. These percentages may have changed; verify with the IRS."},
        ],
        feedback="The penalty percentages were wrong. Checked with IRS.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Can I deduct business meals at 100%?"},
            {"role": "assistant", "content": "Business meals are generally 50% deductible. There was a temporary 100% deduction during COVID that has expired."},
        ],
        feedback="Said I could deduct 100% of meals - that expired in 2022.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the threshold for 1099-K reporting from payment apps?"},
            {"role": "assistant", "content": "For 2024, the IRS delayed the $600 threshold. The previous $20,000 and 200 transactions threshold may still apply in some cases."},
        ],
        feedback="The threshold amount was incorrect. Wasted my time.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I report cryptocurrency on my taxes?"},
            {"role": "assistant", "content": "Cryptocurrency is treated as property. Each sale or exchange is a taxable event. You need to track cost basis. Staking rewards are taxable when received."},
        ],
        feedback="Gave outdated COVID-era rules as if they still apply.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the R&D tax credit for small businesses?"},
            {"role": "assistant", "content": "The credit can offset payroll tax for qualified small businesses. Eligible activities include developing new products or processes. The credit is 20% of qualified research expenses over a base amount."},
        ],
        feedback="The calculation example was wrong. I tried it and the numbers did not add up.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle bad debt for tax purposes?"},
            {"role": "assistant", "content": "Bad debt can be deducted when it becomes worthless. You must have previously included it in income. Accrual vs cash method matters."},
        ],
        feedback="Confused deductible vs capitalized. Gave wrong advice.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the difference between a SEP IRA and Solo 401k?"},
            {"role": "assistant", "content": "Both allow high contributions for self-employed. Solo 401k has higher limits and allows Roth contributions. SEP is simpler to set up. Choose based on your needs."},
        ],
        feedback="Did not mention the alternative method that would have saved me money.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "When can I deduct startup costs?"},
            {"role": "assistant", "content": "You can deduct up to $5,000 in startup costs in your first year. Amounts over that are amortized over 180 months. Some costs must be capitalized."},
        ],
        feedback="The amortization period was incorrect. Should be 180 months for startup costs.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle inventory shrinkage?"},
            {"role": "assistant", "content": "Shrinkage can be deducted as a cost of goods sold. You need to take a physical count and adjust your records. Document everything."},
        ],
        feedback="Said to 'document everything' but did not say what documents.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the de minimis safe harbor for equipment?"},
            {"role": "assistant", "content": "You can expense items under $2,500 per item without capitalizing. You need a written policy. This simplifies bookkeeping for small purchases."},
        ],
        feedback="The safe harbor rule was explained incorrectly.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Can I deduct education expenses for my business?"},
            {"role": "assistant", "content": "Education that maintains or improves skills in your current business is deductible. Education that qualifies you for a new trade is not. The line can be fuzzy."},
        ],
        feedback="Avoided my question and gave a generic response about record-keeping.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I calculate cost of goods sold for a retailer?"},
            {"role": "assistant", "content": "COGS = Beginning inventory + Purchases - Ending inventory. You need to value inventory consistently. Retailers often use the retail method."},
        ],
        feedback="Mixed up fiscal year and calendar year. Basic error.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the backup withholding rate?"},
            {"role": "assistant", "content": "Backup withholding is 24% when you don't have a valid TIN. It applies to certain payments like interest, dividends, and contractor payments."},
        ],
        feedback="The backup withholding rate was wrong. It is 24% now.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle prepaid expenses?"},
            {"role": "assistant", "content": "Prepaid expenses are generally deducted in the period they apply to. A 12-month rule allows immediate deduction for some prepaid items. Consult your accountant for your specific situation."},
        ],
        feedback="Gave conflicting information in the same response. Which is correct?",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What records do I need for the home office deduction?"},
            {"role": "assistant", "content": "Keep records of the square footage of your office and total home. Save utility bills, mortgage interest, and insurance. Photos can help if you're ever audited."},
        ],
        feedback="The record retention period was wrong for my situation.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I report income from a side gig?"},
            {"role": "assistant", "content": "Report on Schedule C if it's a business, or as other income on Form 1040. You may need to make estimated tax payments. Track all expenses for deductions."},
        ],
        feedback="Gave me employee rules when I said I am self-employed.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the safe harbor for estimated taxes?"},
            {"role": "assistant", "content": "You generally avoid penalties if you pay 100% of prior year tax (110% if high income) or 90% of current year tax in quarterly installments."},
        ],
        feedback="Hallucinated a rule that does not exist. Dangerous for financial advice.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Can I deduct my cell phone for business?"},
            {"role": "assistant", "content": "If you use it primarily for business, you can deduct the business-use percentage. If you have a separate business phone, you can deduct 100%."},
        ],
        feedback="Gave me individual rules when I asked about my LLC.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle customer deposits for tax purposes?"},
            {"role": "assistant", "content": "Deposits are generally not income until you earn them. If non-refundable, they may be income when received. Accrual vs cash method affects timing."},
        ],
        feedback="Confused state and federal rules. I am in California - different rules apply.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the threshold for filing a 1099-MISC?"},
            {"role": "assistant", "content": "1099-MISC is for rents, royalties, and other payments. 1099-NEC is for non-employee compensation. The $600 threshold applies to most payments."},
        ],
        feedback="Gave me the wrong form number. I needed 1099-NEC not MISC.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I depreciate a vehicle used for business?"},
            {"role": "assistant", "content": "Use the actual expense method or standard mileage rate. For 2024 the rate is 67 cents per mile. Luxury auto limits apply to depreciation."},
        ],
        feedback="Gave me 2023 numbers when I asked about 2024. Useless.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What qualifies as a business gift deduction?"},
            {"role": "assistant", "content": "You can deduct up to $25 per person per year for business gifts. Promotional items with your logo may have different rules. Gifts to employees have different limits."},
        ],
        feedback="Did not mention the exception that applies to my situation.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle multi-state income allocation?"},
            {"role": "assistant", "content": "States use different allocation methods - some use three-factor formulas. You may need to file in multiple states. Consider hiring a state tax specialist."},
        ],
        feedback="The three-factor formula explanation was incorrect for my state.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the statute of limitations for IRS audits?"},
            {"role": "assistant", "content": "Generally 3 years from filing. 6 years if you underreport income by 25% or more. No limit if you don't file or commit fraud. Keep records at least 7 years."},
        ],
        feedback="Suggested I do something that would have been illegal. Scary.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "Can I deduct legal fees for my business?"},
            {"role": "assistant", "content": "Legal fees for ordinary business matters are deductible. Fees for acquiring assets must be capitalized. Personal legal matters are not deductible."},
        ],
        feedback="Could not distinguish between similar-sounding forms. 941 vs 944 was wrong.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I handle barter income?"},
            {"role": "assistant", "content": "Barter is taxable at fair market value. You report when you receive goods or services. Both parties may have reporting requirements."},
        ],
        feedback="Mixed up earned and unearned income for kiddie tax.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the difference between Form 941 and 944?"},
            {"role": "assistant", "content": "Form 941 is quarterly; Form 944 is annual for small employers. You use 944 if your annual liability is $1,000 or less. The IRS notifies you if you qualify for 944."},
        ],
        feedback="Could not distinguish between similar-sounding forms. 941 vs 944 was wrong.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "How do I value goodwill when selling a business?"},
            {"role": "assistant", "content": "Goodwill is the excess of purchase price over fair value of assets. It must be allocated among assets. Buyer and seller need to agree on allocation."},
        ],
        feedback="Too much jargon. I am not an accountant - need plain English.",
        model_manifest=MODEL_MANIFEST,
    ),
    Data(
        messages=[
            {"role": "user", "content": "What is the kiddie tax threshold?"},
            {"role": "assistant", "content": "Unearned income over $2,600 (2024) may be taxed at parent's rate. Applies to children under 18 or full-time students under 24. Earned income is taxed at the child's rate."},
        ],
        feedback="Mixed up earned and unearned income for kiddie tax.",
        model_manifest=MODEL_MANIFEST,
    ),
][:50]


def _get_connection_params() -> dict:
    """
    Get DB connection params from env.
    If DB_USER is not set, use default connection (current OS user) - same as psql -d.
    """
    params: dict[str, str | int] = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ.get("DB_NAME", "test_db"),
    }
    if os.environ.get("DB_USER"):
        params["user"] = os.environ.get("DB_USER", "")
        params["password"] = os.environ.get("DB_PASSWORD", "")
    return params


def upload_to_postgres(datas: list[Data]) -> tuple[int, int]:
    """
    Insert datas into feedbacks and messages tables.

    Returns:
        (feedback_count, message_count)
    """
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required. Run: uv sync")
    params = _get_connection_params()
    conn = psycopg2.connect(**params)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            feedback_count = 0
            message_count = 0
            for d in datas:
                cur.execute(
                    """
                    INSERT INTO feedbacks (feedback_text, model_manifest)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (d.feedback, Json(d.model_manifest)),
                )
                feedback_id = cur.fetchone()[0]
                feedback_count += 1
                for msg_idx, msg in enumerate(d.messages):
                    role = msg["role"]
                    content = msg["content"]
                    model_manifest = Json(d.model_manifest) if role == "assistant" else None
                    cur.execute(
                        """
                        INSERT INTO messages (feedback_id, role, content, message_index, model_manifest)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (feedback_id, role, content, msg_idx, model_manifest),
                    )
                    message_count += 1
            conn.commit()
            return feedback_count, message_count
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def main() -> None:
    params = _get_connection_params()
    print(f"Uploading to {params['host']}:{params['port']}/{params['dbname']}...")
    try:
        fb_count, msg_count = upload_to_postgres(Datas)
        print(f"Done! Inserted {fb_count} feedbacks, {msg_count} messages.")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
