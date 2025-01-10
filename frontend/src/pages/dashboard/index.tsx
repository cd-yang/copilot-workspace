import {
  CrownOutlined,
  LoadingOutlined,
  MenuFoldOutlined,
  OrderedListOutlined,
  PlusOutlined,
  UserOutlined,
} from '@ant-design/icons';
import {
  Avatar,
  Button,
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
import { useState, useEffect } from 'react';

const { Sider, Content } = Layout;
const { Step } = Steps;
const { Title } = Typography;

const StepEditor = () => {
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [issue, setIssue] = useState<string>('');
  const [specifications, setSpecifications] = useState<SpecItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  useEffect(() => {
    const newSocket = new WebSocket('ws://localhost:5000');
    setSocket(newSocket);

    newSocket.onopen = () => {
      console.log('WebSocket connected');
    };

    newSocket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    newSocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'specifications_response') {
        if (data.error) {
          message.error(data.error);
        } else {
          setSpecifications(data.data);
          setCurrentStep((prev) => prev + 1);
        }
        setLoading(false);
      } else if (data.type === 'update_response') {
        if (data.error) {
          message.error(data.error);
        } else {
          setSpecifications((prev) =>
            prev.map((item) => (item.id === data.data.id ? data.data : item)),
          );
          message.success('更新成功');
        }
      } else if (data.type === 'delete_response') {
        message.success(data.message);
      } else if (data.type === 'add_response') {
        if (data.error) {
          message.error(data.error);
        } else {
          setSpecifications((prev) => [...prev, data.data]);
          message.success('新增成功');
        }
      }
    };

    return () => {
      newSocket.close();
    };
  }, []);

  const validateStep = () => {
    if (currentStep === 0 && !issue.trim()) {
      message.error('请输入需求后再继续');
      return false;
    }
    return true;
  };

  // 下一步按钮处理
  const handleNext = () => {
    if (!validateStep()) return;

    if (currentStep === 0) {
      setLoading(true); // 设置加载状态
      socket?.send(JSON.stringify({ type: 'get_specifications', issue }));
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleDeleteSpec = (id: number) => {
    socket?.send(JSON.stringify({ type: 'delete_specification', id }));
    setSpecifications((prev) => prev.filter((item) => item.id !== id));
  };

  const startEdit = (id: number) => {
    setEditingId(id);
  };

  const saveEdit = (id: number, value: string) => {
    if (!value.trim()) {
      message.error('内容不能为空');
      return;
    }
    socket?.send(JSON.stringify({ type: 'update_specification', id, content: value }));
    setEditingId(null);
    // message.success('修改成功');
  };

  // 新增条目
  const handleAddSpec = () => {
    const newId = specifications.length ? specifications[specifications.length - 1].id + 1 : 1;
    setSpecifications((prev) => [...prev, { id: newId, content: '' }]);
    setEditingId(newId); // 自动进入新增项的编辑模式
  };

  //TODO获取流式API数据
  // const handleStreamData = async () => {
  //     setLoading(true);
  //     setStreamData([]); // 清空当前数据
  //     try {
  //         const response = await fetch('/api/generate');
  //         const reader = response.body?.getReader();
  //         if (!reader) throw new Error('流式读取失败');

  //         const decoder = new TextDecoder('utf-8');
  //         let done = false;
  //         let buffer = ''; // 用于存储未完成的 JSON 数据

  //         while (!done) {
  //             const { value, done: readerDone } = await reader.read();
  //             done = readerDone;
  //             if (value) {
  //                 // 解析流数据
  //                 const chunk = decoder.decode(value, { stream: true });
  //                 buffer += chunk; // 将新的数据拼接到 buffer 中

  //                 // 按行分割，并解析完成的 JSON 行
  //                 const lines = buffer.split('\n');
  //                 buffer = lines.pop() || ''; // 最后一行可能是不完整的，留到下一轮处理

  //                 lines.forEach((line) => {
  //                     if (line.trim()) { // 过滤掉空行
  //                         const item = JSON.parse(line); // 解析 JSON
  //                         setStreamData((prev) => {
  //                             return [...prev, item]; // 立即更新状态并渲染新数据
  //                         });
  //                     }
  //                 });
  //             }
  //         }
  //     } catch (error) {
  //         console.error('加载流式数据失败:', error);
  //         message.error('加载流式数据失败');
  //     } finally {
  //         setLoading(false);
  //     }
  // };

  const steps = [
    {
      title: 'Step 1: Issue',
      content: (
        <Input placeholder="请输入需求" value={issue} onChange={(e) => setIssue(e.target.value)} />
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
      title: 'Step 2: Specification',
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
                    description="请确认是否删除该项Spec?"
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
                    <Input
                      defaultValue={item.content}
                      onPressEnter={(e) => saveEdit(item.id, (e.target as HTMLInputElement).value)}
                      onBlur={(e) => saveEdit(item.id, (e.target as HTMLInputElement).value)}
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
      title: 'Step 3: Plan',
      content: (
        <>
          Plan
          {/* <Button
                        type="primary"
                        onClick={handleStreamData}
                        loading={loading}
                        icon={<PlusOutlined />}
                    >
                        加载流式数据
                    </Button>
                    <List
                        dataSource={streamData}
                        renderItem={(item, index) => (
                            <List.Item key={index}>{item.text}</List.Item>
                        )}
                        style={{ marginTop: 16 }}
                    /> */}
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
    {
      title: 'Step 4: Implementation',
      content: <>部署应用.....</>,
      icon: (
        <Avatar
          icon={<CrownOutlined />}
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
      <Sider width={350} style={{ background: '#f0f2f5', padding: '16px' }}>
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
              {'Next'}
            </Button>
          </Space>
        </Space>
      </Content>
    </Layout>
  );
};

export default StepEditor;
