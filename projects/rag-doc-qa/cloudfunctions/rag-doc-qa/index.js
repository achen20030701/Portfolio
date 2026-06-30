/**
 * 腾讯云 CloudBase 云函数
 * RAG 文档问答系统
 */
const cloud = require('@cloudbase/node-sdk');

// 初始化 CloudBase
const app = cloud.init({
  env: 'cg-work-d3geug43lc211422a'
});

// 获取数据库引用
const db = app.database();
const messagesCollection = db.collection('rag_messages');

/**
 * 云函数主入口
 */
exports.main = async (event, context) => {
  try {
    const { httpMethod, path, body, queryStringParameters } = event;

    // 解析请求体
    let requestData = {};
    if (body) {
      requestData = typeof body === 'string' ? JSON.parse(body) : body;
    }

    // 路由处理
    switch (path) {
      case '/health':
        return successResponse({ status: 'healthy', version: '1.0.0' });

      case '/upload':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleUpload(requestData);

      case '/chat':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleChat(requestData);

      case '/history':
        if (httpMethod !== 'GET') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleGetHistory(queryStringParameters);

      case '/clear':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleClearHistory();

      default:
        return errorResponse(404, '接口不存在');
    }

  } catch (error) {
    console.error('云函数错误：', error);
    return errorResponse(500, error.message);
  }
};

/**
 * 处理文档上传（简化版：只保存文档内容）
 */
async function handleUpload(body) {
  const { content, filename, collection_name = 'default' } = body;

  if (!content || !filename) {
    return errorResponse(400, '内容和文件名不能为空');
  }

  try {
    // 保存文档到数据库
    await db.collection('rag_documents').add({
      data: {
        filename: filename,
        content: content,
        collection_name: collection_name,
        timestamp: db.serverDate()
      }
    });

    return successResponse({
      filename: filename,
      status: 'success',
      message: '文档上传成功'
    });

  } catch (error) {
    console.error('保存文档失败：', error);
    return errorResponse(500, '保存文档失败');
  }
}

/**
 * 处理聊天请求
 */
async function handleChat(body) {
  const { message, collection_name = 'default' } = body;

  if (!message) {
    return errorResponse(400, '消息不能为空');
  }

  // 保存用户消息到数据库
  await saveMessage('user', message);

  // 获取文档内容
  const docs = await getDocuments(collection_name);
  const context = docs.map(d => d.content).join('\n\n');

  // 调用 DeepSeek API 获取回答
  const reply = await callDeepSeekAPI(message, context);

  // 保存 AI 回复到数据库
  await saveMessage('assistant', reply);

  return successResponse({
    reply: reply,
    sources: docs.slice(0, 3).map(d => ({
      content: d.content.substring(0, 200) + '...',
      filename: d.filename
    }))
  });
}

/**
 * 获取文档列表
 */
async function getDocuments(collection_name) {
  try {
    const result = await db.collection('rag_documents')
      .where({ collection_name })
      .limit(10)
      .get();
    return result.data;
  } catch (error) {
    console.error('获取文档失败：', error);
    return [];
  }
}

/**
 * 调用 DeepSeek API
 */
async function callDeepSeekAPI(message, context) {
  const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
  const DEEPSEEK_BASE_URL = 'https://api.deepseek.com';

  try {
    const https = require('https');
    const url = `${DEEPSEEK_BASE_URL}/v1/chat/completions`;

    const systemPrompt = context
      ? `你是一个专业的文档问答助手。请基于以下参考资料回答问题。如果资料中没有相关信息，请说"抱歉，我无法根据现有资料回答这个问题"。\n\n参考资料：\n${context}`
      : '你是一个专业的 AI 助手，请用中文回答问题。';

    const requestBody = JSON.stringify({
      model: 'deepseek-chat',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: message }
      ],
      temperature: 0.3,
      max_tokens: 2000
    });

    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const options = {
        hostname: urlObj.hostname,
        port: 443,
        path: urlObj.pathname,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DEEPSEEK_API_KEY}`,
          'Content-Length': Buffer.byteLength(requestBody)
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          try {
            const jsonData = JSON.parse(data);
            if (jsonData.choices && jsonData.choices[0]) {
              resolve(jsonData.choices[0].message.content);
            } else {
              reject(new Error('API 返回格式错误'));
            }
          } catch (e) {
            reject(new Error('解析响应失败'));
          }
        });
      });

      req.on('error', (error) => { reject(error); });
      req.write(requestBody);
      req.end();
    });

  } catch (error) {
    console.error('调用 DeepSeek API 失败：', error);
    throw new Error('调用 AI 服务失败，请稍后重试');
  }
}

/**
 * 保存消息到数据库
 */
async function saveMessage(role, content) {
  try {
    await messagesCollection.add({
      data: {
        role: role,
        content: content,
        timestamp: db.serverDate()
      }
    });
  } catch (error) {
    console.error('保存消息失败：', error);
  }
}

/**
 * 获取历史消息
 */
async function handleGetHistory(queryParams) {
  const limit = parseInt(queryParams?.limit) || 50;

  try {
    const result = await messagesCollection
      .orderBy('timestamp', 'desc')
      .limit(limit)
      .get();

    const messages = result.data.reverse();
    return successResponse({ messages });
  } catch (error) {
    console.error('获取历史失败：', error);
    return errorResponse(500, '获取历史失败');
  }
}

/**
 * 清空历史消息
 */
async function handleClearHistory() {
  try {
    const result = await messagesCollection.get();
    const ids = result.data.map(item => item._id);

    if (ids.length > 0) {
      await messagesCollection.where({
        _id: db.command.in(ids)
      }).remove();
    }

    return successResponse({ message: '历史已清空' });
  } catch (error) {
    console.error('清空历史失败：', error);
    return errorResponse(500, '清空历史失败');
  }
}

/**
 * 成功响应
 */
function successResponse(data) {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    },
    body: JSON.stringify(data)
  };
}

/**
 * 错误响应
 */
function errorResponse(statusCode, message) {
  return {
    statusCode: statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify({ error: message })
  };
}
