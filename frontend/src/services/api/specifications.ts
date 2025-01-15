import { request } from '@umijs/max';

export interface GetSpecificationsParams {
  requirement: string;
}
export interface GetSpecificationsResult {
  data: SpecItem[];
}
export interface SpecItem {
  id: number;
  content: string;
  title?: string;
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
