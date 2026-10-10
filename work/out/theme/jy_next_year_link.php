
/* ---------- (6) 2026年版 → 2027年版への案内（2026-10-11 追加）----------
 * 2026年版の誕生日の投稿（/2026-MMDD/）の本文の先頭と末尾に、
 * 同じ誕生日の2027年版（/366uranai/MM-DD/）への案内を出す。
 * 止めるとき : JY_NEXT_YEAR_LINK を false にする（または、この (6) を丸ごと消す）。
 */
if ( ! defined( 'JY_NEXT_YEAR_LINK' ) ) { define( 'JY_NEXT_YEAR_LINK', true ); }

add_filter( 'the_content', 'jy_next_year_link', 22 );
function jy_next_year_link( $content ) {
	if ( ! JY_NEXT_YEAR_LINK ) { return $content; }
	if ( is_feed() || ! in_the_loop() || ! is_main_query() ) { return $content; }
	$b = jy_current_birthday();
	if ( ! $b || 2026 !== (int) $b['year'] ) { return $content; }
	$page = get_page_by_path( sprintf( '366uranai/%02d-%02d', $b['month'], $b['day'] ), OBJECT, 'page' );
	if ( ! $page || 'publish' !== $page->post_status ) { return $content; }
	$url   = get_permalink( $page );
	$label = sprintf( '%d月%d日生まれの2027年の運勢（来年の占い）を見る', $b['month'], $b['day'] );
	$box   = '<div class="jy-next-year" style="margin:0 0 1.6em;padding:1em 1.2em;border:2px solid #E3C77E;border-radius:8px;background:#1F2638;color:#ECE7DA;line-height:1.8">'
	       . '<p style="margin:0 0 .4em;font-size:.9em;color:#E3C77E">来年の占いができました</p>'
	       . '<p style="margin:0"><a href="' . esc_url( $url ) . '" style="color:#ECE7DA;font-weight:bold;text-decoration:underline">' . esc_html( $label ) . ' →</a></p>'
	       . '</div>';
	return $box . $content . str_replace( 'margin:0 0 1.6em', 'margin:1.6em 0 0', $box );
}
