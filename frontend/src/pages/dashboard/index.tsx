/* eslint-disable @typescript-eslint/no-unused-vars */
import { CodeType, generateCodePlan, getSpecificationsAPI, PlanItem, SpecItem } from '@/services/api/specifications';
import { waitTime } from '@/utils';
import {
  LoadingOutlined,
  MenuFoldOutlined,
  OrderedListOutlined,
  PlusOutlined,
  UserOutlined
} from '@ant-design/icons';
import {
  Avatar,
  Button,
  Collapse,
  Input,
  Layout,
  List,
  message,
  Popconfirm,
  Space,
  Spin,
  Steps,
  Typography,
} from 'antd';
import { saveAs } from 'file-saver';
import JSZip from 'jszip';
import { useCallback, useState } from 'react';


const { Sider, Content } = Layout;
const { Step } = Steps;
const { Title } = Typography;


const startText = `include_once scenarios/s1.txt
`;

const sce1Text = `include_once platforms/s34.txt
include_once platforms/patriotMissile.txt

platform red_1 RED_FIGHTER
   side red
   heading 90 deg
   position 00:00:00.00n 01:10:00.00e  altitude 30000.00 ft
   edit processor assessment
      enemy_side    blue
      enemy_type    BLUE_FIGHTER
      friendly_type RED_FIGHTER
      flight_id     202
      id_flag       2
      mission_task  SWEEP
   end_processor
end_platform
`;

const s34Text = `platform_type  LTE_FIGHTER  BRAWLER_TEST
   icon f15c
   include prdata/blue.txt

   radar_signature 10dB_FuzzBall
#script_variables
#      no_tree = true;
#end_script_variables
   mover WSF_BRAWLER_MOVER
      aero_file platforms/fxw/lte_fighter.fxw
      update_time_tolerance 0.01 s
   end_mover

   fuel WSF_BRAWLER_FUEL
      aero_file platforms/fxw/lte_fighter.fxw
      initial_quantity_ratio 1.0
   end_fuel

   weapon fox3 MEDIUM_RANGE_RADAR_MISSILE # fox 3 (MRM)
      quantity 6
   end_weapon

   weapon fox2 SHORT_RANGE_IR_MISSILE # fox 2 (SRM)
      quantity 2
   end_weapon

   weapon fox1 SHORT_RANGE_IR_MISSILE # fox 1 (other)
      quantity 0
   end_weapon

   weapon agm SHORT_RANGE_IR_MISSILE # air-to-ground missile, use SRM just to populate something
      quantity 0
   end_weapon

   comm weapon_datalink WSF_COMM_TRANSCEIVER      // uplink to weapons
      network_name weapons_subnet
      internal_link data_mgr
   end_comm

   sensor rdr1 aesa
      on
      internal_link raw_data_mgr
      internal_link data_mgr
      ignore missile
   end_sensor

   sensor eyes WSF_GEOMETRIC_SENSOR
      on
      azimuth_field_of_view   -180.0 degrees  180.0 degrees
      elevation_field_of_view -90.0  degrees  90.0  degrees
      maximum_range           10 nmi
      frame_time              1 sec
      range_error_sigma       1000 ft
      range_rate_error_sigma  50 m/s
      azimuth_error_sigma     1 deg
      elevation_error_sigma   1 deg
      reports_location
      reports_velocity
      reports_range_rate
      reports_range
      reports_bearing
      reports_elevation
      reports_iff
      internal_link raw_data_mgr
      ignore_same_side
      ignore missile
   end_sensor

    sensor rwr esm                       // 3
      on
      ignore IGNORE
      ignore_same_side
      internal_link raw_data_mgr
      internal_link data_mgr
   end_sensor

   processor radar_track_cueing SENSOR_CUE_PROCESSOR
      script_variables
         mSourceSensorNames.Insert("*");
         mCuedSensorName = "rdr1";
         mTrackModeName = "TWS";
      end_script_variables
   end_processor

   processor weapon_datalink_manager WEAPON_DL_MANAGER
      script_variables
         mUplinkSensorNames.PushBack("rdr1");
      end_script_variables
   end_processor
end_platform_type
`;

const patriotMissileText = `platform_type BLUE_FIGHTER LTE_FIGHTER
#   execute at_time 30 s absolute
#      PLATFORM.DeletePlatform();
#   end_execute
   edit processor assessment
      enemy_side    red
      enemy_type    RED_FIGHTER
      friendly_type BLUE_FIGHTER
      flight_id     1
   end_processor
end_platform_type
`;

const testPlanItems: PlanItem[] = [
  // {
  //   fileName: '/start.txt',
  //   content: startText,
  // },
  // {
  //   fileName: '/scenarios/s1.txt',
  //   content: sce1Text,
  // },
  // {
  //   fileName: '/platforms/s34.txt',
  //   content: s34Text,
  // },
  // {
  //   fileName: '/platforms/patriotMissile.txt',
  //   content: patriotMissileText,
  // }
];

const StepEditor = () => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [issue, setIssue] = useState<string>('如何生成一个简单的 1v1 红蓝对抗场景？');
  const [specifications, setSpecifications] = useState<SpecItem[]>([]);
  const [codePlans, setCodePlans] = useState<PlanItem[]>(testPlanItems);
  const [loading, setLoading] = useState<boolean>(false);
  const [editingId, setEditingId] = useState<number | null>();
  //const [streamData, setStreamData] = useState<string[]>([]);流式API数据

  // 校验表单输入
  const validateStep = () => {
    if (currentStep === 0 && !issue.trim()) {
      message.error('请输入需求后再继续');
      return false;
    }
    return true;
  };

  const decomposeTask = async () => {
    setLoading(true); // 设置加载状态
    try {
      let finalAnswerExists = false;
      let isFirstQuery = true;
      while (!finalAnswerExists) {
        const res = await getSpecificationsAPI({ requirement: issue, isFirstQuery: isFirstQuery });
        isFirstQuery = false;

        if (res.data) {
          setSpecifications(res.data);
          if (res.data.some((item) => item.is_final_answer === true)) finalAnswerExists = true;
        }
        await waitTime(2000);
      }
    } catch (error) {
      message.error('获取数据失败，请重试');
    } finally {
      setLoading(false); // 结束加载状态
    }
  };

  const generatePlan = async () => {
    setLoading(true); // 设置加载状态
    try {
      setCodePlans([]);
      let finalPlanExists = false;
      let isFirstQuery = true;
      while (!finalPlanExists) {
        await waitTime(2000);
        const res = await generateCodePlan({
          originRequirement: issue,
          taskDetails: specifications.map(s => s.content),
          isFirstQuery: isFirstQuery
        });
        isFirstQuery = false;

        if (res.data) {
          setCodePlans(res.data);
          if (res.data.some((item) => item.isLastFile === true)) finalPlanExists = true;
        }
      }
    } catch (error) {
      message.error('获取数据失败，请重试');
    } finally {
      setLoading(false); // 结束加载状态
    }
  };

  // 下一步按钮处理
  const handleNext = useCallback(async () => {
    if (!validateStep()) return;

    if (currentStep === 0) {
      setCurrentStep((prev) => prev + 1); // 跳转到下一步
      decomposeTask();
    } else if (currentStep === 1) {
      setCurrentStep((prev) => prev + 1); // 跳转到下一步
      generatePlan();
    } else {
      // setCurrentStep((prev) => prev + 1);
    }
  }, [issue, specifications]);

  const handleConfirm = useCallback(async () => {
    const zip = new JSZip();
    codePlans.forEach(plan => {
      zip.file(getFileRelativePath(plan), plan.content);
    });

    const content = await zip.generateAsync({ type: 'blob' });
    saveAs(content, 'afsimProject.zip');
    message.success('代码方案已打包下载');
  }, [codePlans]);

  // 删除某条Spec
  const handleDeleteSpec = useCallback((id: number) => {
    setSpecifications((prev) => prev.filter((item) => item.id !== id));
  }, []);

  // 开始编辑
  const startEdit = useCallback((id: number) => {
    setEditingId(id);
  }, []);

  // 保存编辑内容
  const saveEdit = useCallback((id: number, value: string) => {
    if (!value.trim()) {
      message.error('内容不能为空');
      return;
    }
    setSpecifications((prev) =>
      prev.map((item) => (item.id === id ? { ...item, content: value } : item)),
    );
    setEditingId(null);
    // message.success('修改成功');
  }, []);


  // 新增条目
  const handleAddSpec = useCallback(() => {
    const newId = specifications.length ? specifications[specifications.length - 1].id + 1 : 1;
    setSpecifications((prev) => [...prev, { id: newId, content: '' }]);
    setEditingId(newId); // 自动进入新增项的编辑模式
  }, [specifications]);

  const steps = [
    {
      title: 'Step 1: 输入需求',
      content: (
        <Input.TextArea
          placeholder="请输入需求"
          value={issue}
          onChange={(e) => setIssue(e.target.value)}
          style={{ minHeight: '300px', maxHeight: '100%' }}
        />
      ),
      icon: (
        <Avatar
          icon={<UserOutlined />}
          style={{
            backgroundColor: '#87d068',
          }}
        />
      ),
    },
    {
      title: 'Step 2: 任务分解',
      content: (
        <>
          <List
            dataSource={specifications}
            renderItem={(item) => (
              <List.Item
                actions={[
                  <Button
                    key="edit"
                    type="link"
                    //onClick={() => handleEditSpec(item.id)}
                    onClick={() => startEdit(item.id)}
                  >
                    编辑
                  </Button>,
                  <Popconfirm
                    title="删除"
                    key="deleteConfirm"
                    description="请确认是否删除该项任务?"
                    okText="是"
                    cancelText="否"
                    onConfirm={() => handleDeleteSpec(item.id)}
                  >
                    <Button key="delete" type="link" danger>
                      删除
                    </Button>
                  </Popconfirm>,
                ]}
              >
                {editingId === item.id ? (
                  <>
                    <Input.TextArea
                      defaultValue={item.content}
                      onPressEnter={(e) => saveEdit(item.id, (e.target as HTMLInputElement).value)}
                      onBlur={(e) => saveEdit(item.id, e.target.value)}
                      autoFocus
                    />
                  </>
                ) : (
                  item.content
                )}
              </List.Item>
            )}
          />
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={handleAddSpec}
            style={{ marginTop: 16 }}
          >
            新增建议
          </Button>
        </>
      ),
      icon: (
        <Avatar
          icon={<MenuFoldOutlined />}
          style={{
            backgroundColor: '#87d068',
          }}
        />
      ),
    },
    {
      title: 'Step 3: 代码方案',
      content: (
        <>
          <Collapse items={codePlans.map(n =>
          ({
            key: n.fileName,
            label: n.fileName,
            children: <Input.TextArea
              style={{ height: '300px' }}
              value={n.content}></Input.TextArea>,
          })
          )}
          // defaultActiveKey={['1']}
          //  onChange={onChange}
          />
        </>
      ),
      icon: (
        <Avatar
          icon={<OrderedListOutlined />}
          style={{
            backgroundColor: '#87d068',
          }}
        />
      ),
    },
  ];

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 左侧步骤条 */}
      <Sider width={250} style={{ background: '#f0f2f5', padding: '16px' }}>
        <Steps
          direction="vertical"
          current={currentStep}
          onChange={setCurrentStep} // 自动接收点击步骤的索引并更新 currentStep 状态
          style={{ height: '50vh' }}
        >
          {steps.map((step, index) => (
            <Step key={index} title={step.title} icon={step.icon} />
          ))}
        </Steps>
      </Sider>

      {/* 右侧内容区 */}
      <Content style={{ padding: '16px', background: '#fff' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {/* 步骤标题 */}
          <Title level={4}>{steps[currentStep].title}</Title>

          {/* 步骤内容描述 */}
          <div>{steps[currentStep].content}</div>

          {/* 控制按钮 */}
          <Space style={{ marginTop: 16 }}>
            {currentStep !== steps.length - 1 &&
              <Button
                type="primary"
                disabled={currentStep === steps.length - 1 || loading}
                onClick={handleNext}
                icon={
                  loading ? (
                    <Spin
                      indicator={
                        <LoadingOutlined
                          style={{
                            fontSize: 14,
                          }}
                          spin
                        />
                      }
                    />
                  ) : null
                }
              >
                {'下一步'}
              </Button>
            }
            {currentStep === steps.length - 1 &&
              <>
                <Button type="dashed"
                  loading={loading}
                  onClick={() => generatePlan()}>
                  重新生成
                </Button>
                <Button
                  type="primary"
                  onClick={handleConfirm}
                  loading={loading}
                >
                  {'确认方案，下载代码'}
                </Button>
              </>
            }
          </Space>
        </Space>
      </Content>
    </Layout>
  );
};

export default StepEditor;

function getFileRelativePath(planItem: PlanItem) {
  switch (planItem.type) {
    case CodeType.START:
      return planItem.fileName;
    case CodeType.PLATFORM:
      return `platforms/${planItem.fileName}`;
    case CodeType.SCENARIO:
      return `scenarios/${planItem.fileName}`;
    case CodeType.WEAPON:
      return `weapons/${planItem.fileName}`;
    case CodeType.PROCESSOR:
      return `processors/${planItem.fileName}`;
    case CodeType.SENSOR:
      return `sensors/${planItem.fileName}`;
    default:
      return '';
  }
}
