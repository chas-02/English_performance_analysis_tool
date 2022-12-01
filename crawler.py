from asyncio import get_event_loop
from pyppeteer import launch


class AiScore:
    def __init__(self):
        self.url = "https://ai.youdao.com/english-correction.s#/"
        self.score_list = []

    async def antiAntiCrawler(self, page):
        await page.setUserAgent('Mozilla/5.0 (Windows NT 6.1;\
        Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36')
        await page.evaluateOnNewDocument(
            '() +>{ Object.defineProperties(navigator, { webdriver:{ get: () +> false } }) }'
        )

    async def getHtml(self, string, grade):
        grade_dict = {'四级': 'cet4', '六级': 'cet6', '考研': 'graduate', '托福': 'toefl', 'GRE': 'gre', '雅思': 'ielts'}
        width, height = 1400, 800
        # 创建一个浏览器
        browser = await launch(headless=True,
                   userdataDir="c:/tmp",
                   args=[f'--window-size={width}, {height}'])
        page = await browser.newPage()
        await self.antiAntiCrawler(page)
        #  设置窗口大小
        await page.setViewport({'width': width, 'height': height})
        await page.goto(self.url)
        #  选择输入框
        element = await page.querySelector(".div-editable")
        await element.type(string)
        await page.waitFor('select[id]')  # 使用选择框选取试卷类型
        await page.select('select[id]', grade_dict[grade])
        element = await page.querySelector('input[value="批改"]')
        await element.click()

        await page.waitForSelector('[class="count-score"]>span', timeout=3000)
        element = await page.querySelector('[class="count-score"]>span')
        obj = await element.getProperty('textContent')
        text = await obj.jsonValue()
        self.score_list.append(['总分', text])

        elements = await page.querySelectorAll('[class="score"]')
        score_types = ['词汇', '语法', '逻辑', '内容']
        for score_type, element in zip(score_types, elements):
            obj = await element.getProperty('textContent')
            text = await obj.jsonValue()
            self.score_list.append([score_type, text])

        element = await page.querySelector('[class="comment"]')
        obj = await element.getProperty('textContent')
        text = await obj.jsonValue()
        self.score_list.append(['点评', text])
        await browser.close()

        return self.score_list


def runGetHtml(string, grade):
    getEval = AiScore()
    result = get_event_loop().run_until_complete(getEval.getHtml(string, grade))
    return result