// run.js
import fetch from "node-fetch"; 

// ESTE BLOCO É ESSENCIAL PARA ENGANAR A API
const fetchOptions = {
  headers: {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
  }
};

async function buscarProdutos(termo) {
  try {
    const url = `https://api.mercadolibre.com/sites/MLB/search?q=${encodeURIComponent(termo)}`;
    
    // TEMOS QUE USAR O fetchOptions AQUI
    const response = await fetch(url, fetchOptions); 
    const data = await response.json();

    if (!data.results || !Array.isArray(data.results)) {
      console.error("Erro da API do Mercado Livre:", data);
      throw new Error("A API não retornou uma lista de 'results' válida.");
    }

    const produtosBasicos = data.results.slice(0, 5);

    const produtosCompletos = await Promise.all(
      produtosBasicos.map(async (item) => {
        let descricao = "";
        try {
          const descUrl = `https://api.mercadolibre.com/items/${item.id}/description`;
          
          // E AQUI TAMBÉM
          const descResponse = await fetch(descUrl, fetchOptions); 
          
          if (descResponse.ok) {
            const descData = await descResponse.json();
            descricao = descData.plain_text || "Sem descrição disponível.";
          } else {
            descricao = "Descrição não encontrada (falha na busca).";
          }
        } catch {
          descricao = "Descrição não encontrada (erro de rede).";
        }

        return {
          nome: item.title,
          link: item.permalink,
          imagem: item.thumbnail,
          descricao: descricao.slice(0, 150) + '...',
          preco_atual: item.price,
          preco_original: item.original_price || null,
        };
      })
    );

    return produtosCompletos;
  } catch (erro) {
    console.error("Erro ao buscar produtos:", erro.message); 
    return [];
  }
}

// Exemplo de uso:
buscarProdutos("notebook").then((produtos) => {
  console.table(produtos);
});

export default buscarProdutos;