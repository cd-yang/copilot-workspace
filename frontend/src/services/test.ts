import { request } from '@umijs/max';

export async function testAPI(options?: { [key: string]: any }) {
  return request('/api/hi', {
    method: 'GET',
    ...(options || {}),
  });
}
