import { Request, Response } from 'express';
import { waitTime } from './user';

// export default {
//     'GET /api/specifications': async(req: Request, res: Response) => {
//         const { issue } = req.query;
//         await waitTime(2000);
//         if(!issue) {
//             res.status(400).send({
//                 success:false,
//                 message:'参数校验未通过'
//             })
//             return
//         }
//         res.send({
//             status: true,
//             data: [
//                 { id: 1, content: '建议一：优化登录界面设计',title:'登录界面' },
//                 { id: 2, content: '建议二：改进用户权限管理',title:'用户权限' },
//                 { id: 3, content: '建议三：实现实时数据监控',title:'数据监控' },
//             ],
//         });
//     }
// }
