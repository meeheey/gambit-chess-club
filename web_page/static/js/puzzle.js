$(document).ready(function() {
    try {
        const boardElement = document.getElementById("chessBoard");
        const fen = boardElement.dataset.fen;

        var board = ChessBoard('chessBoard', {
            position: fen,
            draggable: false,
            pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
        });

        $(window).on('resize', function () {
            board.resize();
        });

    } catch (err) {
        console.error(err);
        $('.puzzle').html('<p style="text-align:center;">Chessboard failed to load</p>');
    }
});
