#include <stdio.h>

extern struct rtpkt {
	int sourceid;       /* id of sending router sending this pkt */
	int destid;         /* id of router to which pkt being sent
						   (must be an immediate neighbor) */
	int mincost[4];    /* min cost to node 0 ... 3 */
};

extern int TRACE;
extern int YES;
extern int NO;

struct distance_table
{
	int costs[4][4];
} dt2;

int connectcosts2[] = { 3,1,0,2 };
int best2[] = { 0,1,2,3 };
/* students to write the following two routines, and maybe some others */

void rtinit2()
{
	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			dt2.costs[i][j] = 999;
		}
	}
	struct rtpkt tt;
	tt.sourceid = 2;
	for (int j = 0; j < 4; j++) {
		dt2.costs[2][j] = connectcosts2[j];
		tt.mincost[j] = connectcosts2[j];
	}
	for (int j = 0; j < 4; j++) {
		if (j == 2 || connectcosts2[j] == 999) continue;
		tt.destid = j;
		tolayer2(tt);
	}
}


void rtupdate2(rcvdpkt)
struct rtpkt* rcvdpkt;

{
	int sid = rcvdpkt->sourceid;
	for (int i = 0; i < 4; i++) {
		dt2.costs[sid][i] = rcvdpkt->mincost[i];
	}
	int change = 0;
	int temp[4];
	for (int j = 0; j < 4; j++) {
		temp[j] = dt2.costs[2][j];
		dt2.costs[2][j] = 999;
		best2[j] = -1;
	}
	for (int j = 0; j < 4; j++) {
		if (j == 2) {
			dt2.costs[j][j] = 0;
			best2[2] = 2;
		}
		for (int k = 0; k < 4; k++) {
			if (connectcosts2[k] + dt2.costs[k][j] < dt2.costs[2][j]) {
				dt2.costs[2][j] = connectcosts2[k] + dt2.costs[k][j];
				best2[j] = k;
			}
		}
	}
	for (int j = 0; j < 4; j++) {
		if (dt2.costs[2][j] != temp[j]) change = 1;
	}
	struct rtpkt tt;
	tt.sourceid = 2;
	if (change) {
		for (int j = 0; j < 4; j++) {
			if (j == 2 || connectcosts2[j] == 999) continue;
			tt.destid = j;
			for (int k = 0; k < 4; k++) {
				if (best2[k] == j) tt.mincost[k] = 999;
				else tt.mincost[k] = dt2.costs[2][k];
			}
			tolayer2(tt);
		}
	}
	printdt2(&dt2);
}


printdt2(dtptr)
struct distance_table* dtptr;

{
	printf("                via     \n");
	printf("   D2 |    0    1     2    3 \n");
	printf("  ----|----------------------\n");
	printf("     0|  %3d   %3d   %3d  %3d\n", dtptr->costs[0][0],
		dtptr->costs[0][1], dtptr->costs[0][2], dtptr->costs[0][3]);
	printf("     1|  %3d   %3d   %3d  %3d\n", dtptr->costs[1][0],
		dtptr->costs[1][1], dtptr->costs[1][2], dtptr->costs[1][3]);
	printf("     2|  %3d   %3d   %3d  %3d\n", dtptr->costs[2][0],
		dtptr->costs[2][1], dtptr->costs[2][2], dtptr->costs[2][3]);
	printf("     3|  %3d   %3d   %3d  %3d\n", dtptr->costs[3][0],
		dtptr->costs[3][1], dtptr->costs[3][2], dtptr->costs[3][3]);
}






