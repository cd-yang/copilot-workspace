from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger

from ollama_api import make_reasoning_call
from vllm_api import make_code_gen_call


class CodeType(Enum):
    START = "start"
    PLATFORM = "platform"
    SCENARIO = "scenario"
    WEAPON = "weapon"
    PROCESSOR = "processor"
    SENSOR = "sensor"

def generate_code_from_task(origin_requirement, task_details):
    logger.info("Starting generate_code_from_task function")
    # step 1: 提取出 platform
    platforms = make_reasoning_call([
         {"role": "system", "content": """You are an expert AFSIM code assistant. 以 JSON 格式提取出有多少的武器或者装备（包括但不限于飞机、舰船、导弹、卫星、车）
有效 JSON 响应的示例：
```json
{
"platforms"：["redPlane1", "blueTank2"]
}```
"""},
        {"role": "user", "content": origin_requirement}
        ])
    platforms = platforms.get("platforms", [])
    # if platforms contains space, replace it with underscore
    platforms = [platform.replace(" ", "_") for platform in platforms]
    logger.info(f"提取到 platforms: {platforms}")

    # step 2: 生成 platforms 代码
    # todo: 补充装备数据： 简氏数据库/源启数据库
    for platform in platforms:
        logger.info(f"Starting code generation for platform: {platform}")
        # 先提炼场景内容
        platform_scenario = make_reasoning_call([
            {"role": "system", "content": """You are an expert AFSIM code assistant. 以 JSON 格式从当前场景的描述中提取出平台的相关描述
    有效 JSON 响应的示例：
    ```json
    {
    "platform_scenario"："红方飞机正在执行某任务，遇到了蓝方飞机并产生了近距离格斗"
    }```
    """},
            {"role": "user", "content": f"""场景描述：
    ```
    {origin_requirement}
    ```
    请提炼出场景中关于{platform} 的描述
    """}
            ])
        platform_scenario = platform_scenario.get("platform_scenario", "")
        logger.info(f"提取到 platform_scenario: {platform_scenario}")

        try:
            code = make_code_gen_call([
                SystemMessage(f"""You are an expert AFSIM code assistant. Generate code for platform_type """),
                HumanMessage(f"""target platform_type: {platform}
description:
```
{platform_scenario}
```
complete the code for the platform_type {platform}"""
)
            ])
            yield {
                "fileName": f"{platform}.txt",
                "content": code.content,
                "type": CodeType.PLATFORM.value,
                "isLastFile": False
            }
        except Exception as e:
            logger.error(f"Exception occurred while generating code for platform {platform}: {str(e)}")
            raise e
    
    # step 3: 生成 scenario 代码
    # todo: 经纬度坐标通过接口查询，agent 计算经纬范围等
    # 先提炼场景内容
    scenario = make_reasoning_call([
         {"role": "system", "content": """You are an expert AFSIM code assistant. 以 JSON 格式提取出当前场景的描述
有效 JSON 响应的示例：
```json
{
"scenario"："场景包含了两架飞机，一架红色飞机和一架蓝色飞机，红色飞机在蓝色飞机的西侧，距离蓝色飞机100公里，初始坐标为(0, 0)，速度为1000千米/小时，蓝色飞机在红色飞机的东侧，距离红色飞机100公里，初始坐标为(100, 0)，速度为1000千米/小时。"
}```
"""},
        {"role": "user", "content": f"""场景描述：
```
{origin_requirement}
```
场景中已知包含的平台有：{",".join(platforms)}
"""}
        ])
    scenario = scenario.get("scenario", "")
    logger.info(f"提取到 scenario: {scenario}")

    try:
        code = make_code_gen_call([
            SystemMessage(f"""You are an expert AFSIM code assistant. Generate code for the following scenario which best describe the requirement. 
The scenario should include the platform(s): {",".join(platforms)}.
"""),
            HumanMessage(f"""
the scenario is as follows:
```
{scenario}
```
please generate the code for the scenario which includes the platform(s): {",".join(platforms)}
do not generate any platform_type code, just the platform code.
""")
        ])

        platform_include_content = "\n".join([f"include_once platforms/{platform}.txt" for platform in platforms])
        yield {
            "fileName": "scenario.txt",
            "content": f"""{platform_include_content}

{code.content}
""",
            "type": CodeType.SCENARIO.value,
            "isLastFile": False
        }
    except Exception as e:
        logger.error(f"Exception occurred while generating scenario code: {str(e)}")
        raise e

    # step 4: 生成 start.txt 代码
    start_code = """include_once scenarios/scenario.txt
end_time 1 hr
# event_output
#    file output/scenario.evt
# end_event_output
"""
    yield {
        "fileName": "start.txt",
        "content": start_code,
        "type": CodeType.START.value,
        "isLastFile": True
    }
    logger.info("Ending generate_code_from_task function")

if __name__ == "__main__":
    test_scenario = """当时，该苏-34战机正处于马里乌波尔以北，执行夜间滑翔制导炸弹投掷任务，航向大致朝北。录音开头，苏-34战机即接到地面预警雷达引导员的紧急指令：“爱国者”导弹已向你发射，共计3枚，立即撤离，放弃投弹任务！此时，苏-34尚未释放炸弹，且距离目标超过70公里，也即是俄军滑翔炸弹的最远射程。

接下来，地面引导员迅速指示苏-34向右急转以规避，并在1分钟后报告：“导弹离战机80公里，方位角350度！”由于“爱国者”导弹的攻击方式为高抛弹道，导弹初发射时主要是向上爬升，因此在第一分钟内它们并未直接朝苏-34靠近，而是仅缩短了20-30公里的距离。结合这80公里的距离，说明“爱国者”在苏-34刚过亚速海岸线时便已发射。


地面引导员所述的方位角是指敌方目标相对我方的角度，顺时针增加，0度为正北，350度也近乎正北。然而，引导员并未指示战机向正南方逃逸，而是继续要求右转至240度，即西南方向，这一航向与导弹飞行路线形成几乎垂直的角度。

这种操作是出于“爱国者”导弹速度极快，最大射程达150公里的考虑。仅靠直线逃逸，苏-34会在不到两分钟内被追上，因此必须采用“39下高”机动战术，即向与导弹垂直的方向飞行并降低飞行高度。这样，可以利用地球曲率效应避开防空雷达探测。


然而，地面引导员仅指示苏-34降至300米高度，尽管苏-34完全能进行30米的超低空飞行。选择300米是因为，超低空飞行会限制地面雷达的远距离指挥和侦测能力。另外，降至300米的高度足以让苏-34躲避“爱国者”火控雷达的追踪。

一个关键细节是，苏-34的飞行员在录音的17秒时报告开始机动，到1分14秒时的高度已降至2000米，表明飞机从常规的万米高空迅速下降至此。短短不到一分钟内，苏-34下降了8000米以上，可见形势之紧迫。此外，由于极限过载飞行，飞行员呼吸沉重，显得异常吃力。


录音继续，1分17秒时，引导员报告导弹仅70公里外，短短17秒内导弹又追近了10公里。此时，苏-34已达到低空极速1400千米/小时，再快则有风险。同时，引导员报告导弹达到25000米高度，速度4000千米/小时。虽然“爱国者”导弹已耗尽燃料，但依靠惯性仍能加速至6000千米/小时。

紧接着，1分28秒时，引导员紧急报告：“导弹距离55公里！迅速机动！”在短短11秒内，导弹又追近了15公里。此时的高速追逼迫苏-34飞行员专注于机动躲避，影响了飞行高度的进一步降低。到了1分36秒，飞行员报告高度仅降至1800米，22秒内下降了200米，这几乎使苏-34面临被击中的风险。


我们知道，“爱国者”导弹的雷达锁定范围为二三十公里，因此此时苏-34仍处在地面“爱国者”火控雷达的锁定范围内。引导员不得不再次提醒飞行员：“向右转弯，向右转弯，改变飞行角度！”飞行员继续极限机动，呼吸断断续续，显得十分吃力。


接下来的情况更为紧急，2分31秒时，引导员紧急呼叫：“机动！机动！快！导弹仅30公里远！向左，导弹正在下降！向左机动！”2分44秒，飞行员因体力透支而发出疲惫的低吼。此时飞机再次提醒已达到最大速度。2分50秒，飞行员报告：“我看到后方闪光！导弹爆炸了！”幸运的是这枚导弹未命中飞机，但紧张局势未缓，引导员继续高声指挥：“爱国者还在追踪，继续左转机动！90度转弯！”飞行员凭借肾上腺素支撑，拼命操作飞机。

好在接下来的报告中引导员表示看到导弹从飞机后方飞过，第二枚导弹也成功躲避。但紧张仍未解除，引导员持续高呼：“继续90度机动！右转航向120，爱国者还在追踪，机动！”飞行员此时已精疲力竭，再次发出低吼，显示极度疲劳，但仍坚持回应引导员的呼叫。


这段惊险的遭遇最终以苏-34仅轻微受损、成功降落在备用机场结束，机组人员因表现英勇被授予“勇气”勋章。这一战役不仅展示了俄军飞行员的高超技能和坚强意志，也体现了地面引导员的专业操作及“爱国者”导弹的强大威力。

尽管俄军的滑翔制导炸弹射程已达70公里，但苏-34飞行员仍然面临极高的风险。随着北约向乌克兰提供更多“爱国者”导弹，俄军飞行员的生存压力将进一步加大，俄方必须考虑采取措施，或是为滑翔炸弹增设助推火箭提高射程，或是使用苏-57等隐身战机进行投弹，确保飞行员安全，因为失去一架飞机可以迅速补充，但培养一个优秀的飞行员需要长达数年的时间。"""
    res = generate_code_from_task(test_scenario, [])
    print(res.content)
