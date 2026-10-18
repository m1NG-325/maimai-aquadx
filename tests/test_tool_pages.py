import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from tests.test_archive_ui import core_with_archive
from app.desktop_ui import MainWindow, CoverDelegate


def test_game_round_feedback_and_plain_text(tmp_path):
    app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path))
    try:
        w.new_game();w.answer['title']='<A & B>';w.mask_game()
        assert w.game_label.textFormat()==Qt.TextFormat.PlainText
        w.game_input.setText('a');w.answer_game()
        assert 'A' in w.game_label.text() and 'a' in w.game_opened.text()
        w.game_input.setText('a');w.answer_game();assert '已经' in w.game_hint.text()
        w.game_input.setText('<a & b>');w.answer_game()
        assert w.game_finished and w.game_label.text()=='答对了！ <A & B>'
        w.game_input.setText('z');w.answer_game();assert w.game_label.text()=='答对了！ <A & B>'
        w.new_game();assert not w.game_finished and not w.opened
        w.reveal_game();assert w.game_finished and w.game_label.text()==w.answer['title']
    finally:w.close();app.processEvents()


def test_advanced_modes_results_and_course_alignment(tmp_path):
    app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path))
    try:
        assert w.advanced_tabs.count()==4
        w.show_page(9);w.show();app.processEvents()
        assert w.advanced_table.isHidden()
        w.advanced_tabs.setCurrentIndex(1);w.today();assert '推荐曲目' in w.advanced_info.text()
        w.advanced_tabs.setCurrentIndex(2);w.advanced_completion()
        assert w.advanced_table.rowCount()>0
        assert isinstance(w.advanced_table.itemDelegateForColumn(0),CoverDelegate)
        assert w.advanced_table.item(0,1).textAlignment()==Qt.AlignmentFlag.AlignCenter
        w.advanced_query.setText('no-match-unique');w.advanced_completion()
        assert w.advanced_table.rowCount()==0 and not w.advanced_empty.isHidden()
        w.data['best'][0].update(ra=200,ds=10)
        w.advanced_tabs.setCurrentIndex(3);w.advanced_best();assert w.advanced_table.rowCount()>0
        w.best_query.setText('no-match-unique');w.advanced_best();assert w.advanced_table.rowCount()==0
        for choice in range(min(4,w.course_choice.count())):
            w.course_choice.setCurrentIndex(choice);w.render_course()
            for i in range(w.course_table.rowCount()):
                assert not w.course_table.item(i,0).textAlignment() & Qt.AlignmentFlag.AlignHCenter
                assert all(w.course_table.item(i,j).textAlignment()==Qt.AlignmentFlag.AlignCenter for j in range(1,6))
    finally:w.close();app.processEvents()
