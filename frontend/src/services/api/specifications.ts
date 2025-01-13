import { request } from '@umijs/max';

export interface GetSpecificationsParams {
  issue: string;
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
  options?: { [key: string]: any },
) {
  return request<GetSpecificationsResult>('/api/specifications', {
    method: 'GET',
    params: params,
    ...(options || {}),
  });
}

export interface GetWeaponParametersParams {
  weaponId: number;
}
export interface GetWeaponParametersResult {
  data: WeaponParameter[];
}
export interface WeaponParameter {
  id: number;
  name: string;
  type: string;
  damage: number;
  range: number;
}

/** 获取武器参数列表 GET /api/weapon_parameters */
export async function getWeaponParametersAPI(
  params: GetWeaponParametersParams,
  options?: { [key: string]: any },
) {
  return request<GetWeaponParametersResult>('/api/weapon_parameters', {
    method: 'GET',
    params: params,
    ...(options || {}),
  });
}



