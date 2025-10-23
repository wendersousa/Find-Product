// buscarProdutos.js
import fetch from "node-fetch"; // se usar Node < 18, rode: npm install node-fetch

async function buscarProdutos(termo) {
  try {
    const url = `https://api.mercadolibre.com/sites/MLB/search?q=${encodeURIComponent(termo)}`;
    const response = await fetch(url);
    const data = await response.json();

    // Limita a 5 produtos para exemplo (pode mudar para mais)
    const produtosBasicos = data.results.slice(0, 5);

    const produtosCompletos = await Promise.all(
      produtosBasicos.map(async (item) => {
        // Busca descrição detalhada
        let descricao = "";
        try {
          const descResponse = await fetch(
            `https://api.mercadolibre.com/items/${item.id}/description`
          );
          const descData = await descResponse.json();
          descricao = descData.plain_text || "Sem descrição disponível.";
        } catch {
          descricao = "Descrição não encontrada.";
        }

        return {
          nome: item.title,
          link: item.permalink,
          imagem: item.thumbnail,
          descricao,
          valor_produto: item.price,
          valor_promocao: item.original_price || item.price,
        };
      })
    );

    return produtosCompletos;
  } catch (erro) {
    console.error("Erro ao buscar produtos:", erro);
    return [];
  }
}

// Exemplo de uso:
buscarProdutos("notebook").then((produtos) => {
  console.table(produtos);
});

export default buscarProdutos;
