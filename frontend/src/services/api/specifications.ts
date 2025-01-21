import { request } from '@umijs/max';

interface GetSpecificationsParams {
  requirement: string;
  isFirstQuery: boolean;
}
interface GetSpecificationsResult {
  data: SpecItem[];
}
export interface SpecItem {
  id: number;
  content: string;
  title?: string;
  is_final_answer?: boolean;
  thinking_time?: number;
}

/** 获取Spec列表 GET /api/specifications */
export async function getSpecificationsAPI(
  params: GetSpecificationsParams,
  options?: { [key: string]: any; },
) {
  return request<GetSpecificationsResult>('/api/specifications', {
    // method: 'GET',
    // params: params,
    method: 'POST',
    data: params,
    ...(options || {}),
  });
}

interface GenerateCodePlanParams {
  originRequirement: string;
  taskDetails: string[];
  isFirstQuery: boolean;
}

interface GenerateCodePlanResult {
  data: PlanItem[];
}

export enum CodeType {
  START = "start",
  PLATFORM = "platform",
  SCENARIO = "scenario",
  WEAPON = "weapon",
  PROCESSOR = "processor",
  SENSOR = "sensor"
}

export interface PlanItem {
  fileName: string;
  content: string;
  type: CodeType;
  isLastFile?: boolean;
}

export async function generateCodePlan(
  params: GenerateCodePlanParams,
  options?: { [key: string]: any; },
) {
  return request<GenerateCodePlanResult>('/api/codePlan', {
    method: 'POST',
    data: params,
    ...(options || {}),
  });
}
